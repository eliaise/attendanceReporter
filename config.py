"""
Class to read the configuration file

Author: eliaise
"""
import logging
from configparser import ConfigParser

# Enable logging
import constants

logging.basicConfig(
    format=constants.LOG_FORMAT, level=logging.INFO
)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config/init.ini"


def read() -> dict:
    """Read the config file"""
    logger.info("Reading the configuration file.")
    config = ConfigParser()
    config.read(CONFIG_FILE)

    return {
        "bot_token": config["Telegram"]["BOT_TOKEN"],
        "admin_email": config["Google"]["ADMIN_EMAIL"],
        "db_host": config["MySQL"]["HOST"],
        "db_user": config["MySQL"]["USER"],
        "db_pass": config["MySQL"]["PASS"],
        "db_name": config["MySQL"]["NAME"]
    }
