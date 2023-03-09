"""
Main logic for the bot.

Methods starting with "handle" are for the respective commands issued by the user.
E.g.
    handle_register:    /register
    handle_name:        follow-up to /register command, for handling the user's name

Author: eliaise
"""

import logging

from telegram import (
    Update,
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters, CallbackQueryHandler,
)
from re import search
import config
from connectors import db, ggsheets
import constants

# Enable logging
from workers import sheetWorker

logging.basicConfig(
    format=constants.LOG_FORMAT, level=logging.INFO
)
logger = logging.getLogger(__name__)

# conversation states
NAME, TITLE, DEPARTMENT, RESTART, ERROR, CANCEL = range(6)

# telegram
bot_token = None
drive_token = None


async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the approval or reject response from the IC"""
    query = update.callback_query
    await query.answer()

    # extracting out the title and name
    registrant = search(r'(.*) is', query.message.text).groups()[0]
    stmt = "UPDATE users SET accStatus = ? WHERE userId = ?"

    if query.data.startswith("Approve"):
        result = db.run_update(stmt, (1, registrant))
        if result:
            await query.edit_message_text(text="Approved {}".format(registrant))
            return
    else:
        result = db.run_update(stmt, (-1, registrant))
        if result:
            await query.edit_message_text(text="Rejected {}".format(registrant))
            return

    # error
    await update.message.reply_text("An exception was caught. Please contact the administrator for help.")


async def notify(user_id: int, name: str, title: str, department: str) -> bool:
    """Notifies the relevant person in-charge that there is an outstanding registration request"""
    logger.info("Sending notification to person in-charge of {} department.".format(department))
    bot = Bot(bot_token)

    # create approve or reject buttons
    choices = [
        [
            InlineKeyboardButton("Accept", callback_data="Approve {}".format(user_id)),
            InlineKeyboardButton("Reject", callback_data="Reject {}".format(user_id))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(choices)

    # find the person in-charge
    stmt = "SELECT chatId FROM users where department = %s and role = 'IC'"
    result = db.run_select(stmt, (department,))

    if result:
        # contact this IC
        ic = result[0]
        await bot.send_message(chat_id=ic,
                               text="{} {} is requesting to join your team.".format(title, name),
                               reply_markup=reply_markup
                               )
    else:
        # contact an admin
        stmt = "SELECT chatId FROM users where role = 'Admin' LIMIT 1"
        result = db.run_select(stmt, None)
        if not result:
            logger.error("No admin found.")
            return False

        admin = result[0][0]
        logger.info("Contacting {} for approval.".format(admin))
        await bot.send_message(chat_id=admin,
                               text="{} {} is requesting to join the {} department.".format(title, name, department),
                               reply_markup=reply_markup)

    return True


def finish(user_id, chat_id, name, title, department) -> bool:
    """Finish the registration process."""
    logger.info("Finishing registration for user {}.".format(user_id))

    # finish registration
    logger.info("Finishing registration for user {}".format(user_id))
    stmt = "INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s)"
    return db.run_insert(stmt, (user_id, chat_id, name, title, department, "User", 0))


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Give an error message as a response"""
    logger.info("Unknown exception was caught.")
    await update.message.reply_text("An exception was caught. Please contact the administrator for help.")
    return ConversationHandler.END


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Give a cancellation message"""
    logger.info("Cancelling registration process.")
    await update.message.reply_text("Stopping the registration process.")
    return ConversationHandler.END


async def handle_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's department."""
    user_id = update.message.from_user.id
    department = update.message.text

    # test whether the department is valid
    match = search(constants.REGEX_DEPARTMENT, department)
    if not match:
        logger.info("User {} submitted an invalid department. Restarting...")
        await update.message.reply_text("Department given is invalid. "
                                        "Please give a valid department. E.g. IT")
        return DEPARTMENT

    logger.info("Saving {} as the department for user {}".format(department, user_id))
    context.user_data["department"] = department
    await update.message.reply_text("Okay! Finalising registration.")
    success = finish(
        user_id,
        update.message.chat.id,
        context.user_data["name"],
        context.user_data["title"],
        context.user_data["department"]
    )

    if not success:
        await update.message.reply_text("An exception was caught. Please contact the administrator for help.")
    else:
        await update.message.reply_text("Successfully registered you into the database. "
                                        "Please wait a few hours for approval.")

    # notify the IC to approve the request
    result = await notify(
        user_id,
        context.user_data["name"],
        context.user_data["title"],
        context.user_data["department"])
    if not result:
        logger.info("Failed to find someone to notify.")

    return ConversationHandler.END


async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's title."""
    user_id = update.message.from_user.id
    title = update.message.text.upper()

    # test whether this title is valid
    match = search(constants.REGEX_TITLE, title)
    if not match:
        logger.info("User {} submitted an invalid title. Restarting...")
        await update.message.reply_text("Title given is invalid. "
                                        "Please give a valid title. E.g. exec")
        return TITLE

    logger.info("Saving {} as the title for user {}".format(title, user_id))
    context.user_data["title"] = title
    await update.message.reply_text("What is your department?")
    return DEPARTMENT


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's name."""
    user_id = update.message.from_user.id
    name = update.message.text

    # test whether this name is valid
    match = search(constants.REGEX_NAME, name)
    if not match:
        logger.info("User {} submitted an invalid name. Restarting...")
        await update.message.reply_text("Name given contains invalid characters or is too long. "
                                        "Please give a valid name.")
        return NAME

    logger.info("Saving {} as the name for user {}".format(name, user_id))
    context.user_data["name"] = name
    await update.message.reply_text("What is your title?")
    return TITLE


async def handle_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the registration process of the user."""
    # get user's telegram id
    user_id = update.message.from_user.id
    logger.info("Starting user registration for user {}".format(user_id))

    # check if this user exists in database
    stmt = "SELECT name, accStatus FROM users WHERE userId = %s"
    result = db.run_select(stmt, (user_id,))

    if result:
        logger.info("User {} exists in database".format(user_id))
        name, acc_status = result[0]
        logger.info(acc_status)
        if acc_status == 1:
            await update.message.reply_text(
                "Hello {}. You have already been registered into the database.".format(name))
        elif acc_status == -1:
            await update.message.reply_text(
                "Hello {}. Your application has been rejected. Please contact your supervisor.".format(name))
        else:
            logger.info("User {}'s account is pending approval")
            await update.message.reply_text("Hello {}. Your account is pending approval. "
                                            "Please check back in a few hours.".format(name))
        return ConversationHandler.END

    # user does not exist in database, query user for information
    await update.message.reply_text("Welcome! We'll begin the registration process. "
                                    "Do a /cancel at any time to exit the registration process. "
                                    "Please give me your name. Only alphabets and spaces are allowed.")
    return NAME


async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the user's status update."""
    user_id = update.message.from_user.id
    status = update.message.text
    logger.info("Updating the status to {} for user {}".format(status, user_id))

    # TODO: update user's status


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prints out the help message."""
    await update.message.reply_text("This bot is updates your attendance. "
                                    "/register: starts the registration process "
                                    "/update <status>: sets your status for the day"
                                    "/pull: displays the attendance of all members in your department "
                                    "/role <role> <user>: sets the role of the target user "
                                    "/help: prints this message")


def main() -> None:
    """Starts the bot."""
    global bot_token, drive_token

    # read the config file
    configs = config.read()
    bot_token = configs.get("bot_token")
    drive_token = configs.get("drive_token")

    # connect to the database
    db.connect(configs)

    # start telegram application object
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("update", handle_update))
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("register", handle_register)],
        states={
            NAME: [MessageHandler(filters.TEXT, handle_name)],
            TITLE: [MessageHandler(filters.TEXT, handle_title)],
            DEPARTMENT: [MessageHandler(filters.TEXT, handle_department)],
            RESTART: [CommandHandler("restart", handle_register)],
            ERROR: [CommandHandler("error", handle_error)],
            CANCEL: [CommandHandler("cancel", handle_cancel)]
        },
        fallbacks=[MessageHandler(filters.TEXT, handle_error)]
    )

    application.add_handler(registration_handler)
    application.add_handler(CallbackQueryHandler(handle_notify, pattern='^(Approve|Reject) [1-9]{1,}$'))

    # create spreadsheet, and schedule subsequent creation of spreadsheets
    ggsheets.connect()
    sheetWorker.init(configs.get('admin_email'))

    # poll for updates
    application.run_polling()


if __name__ == "__main__":
    main()
