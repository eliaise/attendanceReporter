"""
Class to read the configuration file

Author: eliaise
"""
import logging
from configparser import ConfigParser

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
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
        "drive_token": config["Google"]["DRIVE_TOKEN"],
        "db_host": config["MySQL"]["HOST"],
        "db_user": config["MySQL"]["USER"],
        "db_pass": config["MySQL"]["PASS"],
        "db_name": config["MySQL"]["NAME"]
    }
