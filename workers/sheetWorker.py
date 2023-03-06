"""
Worker class to handle creation of a new sheet every day.

Author: eliaise
"""

import schedule
import logging
import constants
from connectors import ggsheets

# Enable logging
logging.basicConfig(
    format=constants.LOG_FORMAT, level=logging.INFO
)
logger = logging.getLogger(__name__)


def create_sheet(admin=None) -> None:
    """Worker function to create a new sheet the following day"""
    logger.info("Creating new worksheet")
    ggsheets.create(admin)


def init(admin=None) -> None:
    """
    Scheduled task to create a new sheet every day.
    """
    logger.info("Creating daily worker.")
    schedule.every().day.at("04:00").do(lambda: create_sheet(admin))
