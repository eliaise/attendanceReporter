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


def create(admin=None) -> None:
    """Create a new spreadsheet"""
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
    except gspread.exceptions.WorksheetNotFound:
        logger.info("Worksheet not found. Creating.")
        sheet = book.add_worksheet(title=constants.SHEET_NAME, rows=constants.SHEET_ROWS, cols=constants.SHEET_COLUMNS)


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
    book = connection.open(book_name)


def main() -> None:
    """Main method for testing"""

    connect()
    create()
    append([["EXEC", "John Doe", "IT", "Present"]])
    update_cell("D1", "Leave")


if __name__ == "__main__":
    main()
