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
book = None        # the target book
book_name = None   # the target book name, updated daily


def create(admin=None) -> None:
    """Create a new spreadsheet"""
    logger.info("Creating new spreadsheet.")
    global book, book_name, connection

    book_name = date.today().strftime(constants.SHEET_NAME)

    # check if workbook exists
    try:
        book = connection.open(book_name)
        logger.info("Workbook found. Returning.")
        return
    except gspread.exceptions.SpreadsheetNotFound:
        logger.info("Workbook not found. Continuing.")

    book = connection.create(book_name)

    # share workbook with admin to allow viewing
    if not admin:
        logger.info("Sharing with admin at {}".format(admin))
        book.share(admin, perm_type='user', role='writer')


def update_cell(cell: str, cell_data: str) -> None:
    """Updates the target cell"""
    logger.info("Updating cell {}".format(cell))
    global book

    if book is None:
        logger.error("Workbook not created.")
        exit(1)

    sheet = book.worksheet("Sheet1")
    sheet.update_acell(cell, cell_data)


def append(data: list) -> None:
    """Appends data to the workbook"""
    logger.info("Appending rows to workbook.")
    global book, book_name

    try:
        book = connection.open(book_name)
    except gspread.exceptions.SpreadsheetNotFound:
        # Recoverable.
        logger.info("Workbook not found. Creating.")
        create()

    sheet = book.worksheet("Sheet1")
    sheet.append_rows(values=data)


def connect() -> None:
    """Connects to the Google Drive via the service account"""
    logger.info("Connecting to the Google Drive.")
    global connection

    connection = gspread.service_account(filename='../config/gg_creds.json')


def main() -> None:
    """Main method for testing"""
    global book

    connect()
    create()
    append([["EXEC", "John Doe", "IT", "Present"]])
    update_cell("D1", "Leave")


if __name__ == "__main__":
    main()
