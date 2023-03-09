"""
Worker class to handle creation of a new sheet every day.

Author: eliaise
"""

import schedule
import logging
import constants
from connectors import ggsheets, db

# Enable logging
logging.basicConfig(
    format=constants.LOG_FORMAT, level=logging.INFO
)
logger = logging.getLogger(__name__)


def create_sheet(admin=None) -> None:
    """Worker function to create a new sheet the following day"""
    logger.info("Creating new worksheet")
    result = ggsheets.create(admin)
    if result == 0:
        # spreadsheet was freshly created, fill up the spreadsheet with data of all users
        # TODO: sort by title and department of user
        stmt = constants.SELECT_ACTIVE_USERS
        result = db.run_select(stmt, None)
        if not result:
            logger.error("Failed to retrieve data for all users.")

        ggsheets.append(result[1:])
        ggsheets.values = result

    ggsheets.append(result[1:])
    ggsheets.values = result


def init(admin=None) -> None:
    """
    Scheduled task to create a new sheet every day.
    """
    # attempt to create new sheet
    create_sheet(admin)

    # schedule next sheet creation
    logger.info("Creating daily worker.")
    schedule.every().day.at("04:00").do(lambda: create_sheet(admin))
