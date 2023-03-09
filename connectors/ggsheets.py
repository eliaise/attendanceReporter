"""
Class for creating and updating Google spreadsheets

Author: eliaise
"""
import gspread
import logging
from datetime import date

import config
import constants

# Enable logging
logging.basicConfig(
    format=constants.LOG_FORMAT, level=logging.INFO
)
logger = logging.getLogger(__name__)

connection = None
book_name = None    # the target book name, updated daily
sheet_name = None   # the target sheet name, updated monthly

values = None       # values in all rows and columns


def locate(user_id: str) -> str:
    """
    Returns the cell for the requested user_id

    Possible error values:
        empty: values is empty
        not_found: unable to find the requested user
    """
    logger.info("Locating user {}".format(user_id))
    row_num = 2         # first row is index 1, which is the header

    if not values:
        logger.info("Values is empty.")
        return "empty"

    for row in values:
        if row[0] == user_id:
            return "D{}".format(row_num)
        row += 1

    # user is not found
    # possible 2 reasons:
    # 1. user does not exist (checks should have been done before calling this function)
    # 2. user's account status was updated after the creation of the spreadsheet
    return "not_found"


def create(admin=None) -> int:
    """
    Create a new spreadsheet

    Returns the following status code:
        0: created
        1: worksheet exists
    """
    logger.info("Creating new spreadsheet.")
    global book_name, sheet_name, connection

    book_name = date.today().strftime(constants.WORKBOOK_NAME)
    sheet_name = date.today().strftime(constants.SHEET_NAME)
    book = None
    sheet = None

    # check if workbook exists
    try:
        book = connection.open(book_name)
        logger.info("Workbook found.")
    except gspread.exceptions.SpreadsheetNotFound:
        logger.info("Workbook not found. Creating and sharing with admin")
        book = connection.create(book_name)

        # share workbook with admin to allow viewing
        if not admin:
            logger.info("Sharing with admin at {}".format(admin))
            book.share(admin, perm_type='user', role='writer')

    # check if worksheet exists
    try:
        sheet = book.worksheet(sheet_name)
        logger.info("Worksheet found.")

        return 1
    except gspread.exceptions.WorksheetNotFound:
        logger.info("Worksheet not found. Creating.")
        sheet = book.add_worksheet(title=constants.SHEET_NAME, rows=constants.SHEET_ROWS, cols=constants.SHEET_COLUMNS)

    return 0


def update_cell(cell: str, cell_data: str) -> None:
    """Updates the target cell"""
    logger.info("Updating cell {}".format(cell))
    global book_name, sheet_name, connection
    book = None
    sheet = None

    try:
        book = connection.open(book_name)
        sheet = book.worksheet(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error("Workbook not found.")
        exit(1)
    except gspread.exceptions.WorksheetNotFound:
        logger.error("Worksheet not found.")
        exit(1)

    sheet.update_acell(cell, cell_data)


def append(data: list) -> None:
    """Appends data to the workbook"""
    logger.info("Appending rows to workbook.")
    global book_name, connection
    book = None
    sheet = None

    try:
        book = connection.open(book_name)
    except gspread.exceptions.SpreadsheetNotFound:
        # Recoverable.
        logger.info("Workbook not found. Creating.")
        create()

    try:
        sheet = book.worksheet(constants.SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        # shouldn't happen, but doesn't hurt to be safe
        logger.error("Worksheet not found.")
        exit(1)

    sheet.append_rows(values=data)


def connect() -> None:
    """Connects to the Google Drive via the service account"""
    logger.info("Connecting to the Google Drive.")
    global connection

    connection = gspread.service_account(filename='../config/gg_creds.json')


def main() -> None:
    """Main method for testing"""

    connect()
    create()
    append([["EXEC", "John Doe", "IT", "Present"]])
    update_cell("D1", "Leave")


if __name__ == "__main__":
    main()
