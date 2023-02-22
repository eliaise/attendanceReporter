"""
Class for interacting with the database.

Author: eliaise
"""
import logging
import mysql.connector

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# mysql connection
connection = None


def run_select(stmt: str, variables: tuple) -> list:
    """Run a select statement."""
    logger.info("SELECT query sent to database: {}".format(stmt))

    result = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(stmt, variables)
            result = cursor.fetchall()
    except Exception as e:
        logger.exception(e)

    return result


def run_insert(stmt: str, variables: tuple) -> bool:
    """Run an insert statement"""
    logger.info("INSERT query sent to database: {}".format(stmt))

    try:
        with connection.cursor() as cursor:
            cursor.execute(stmt, variables)
            connection.commit()
    except Exception as e:
        logger.exception(e)
        return False

    return True


def run_update(stmt: str, variables: tuple) -> bool:
    """Run an update statement"""
    logger.info("UPDATE query sent to database: {}".format(stmt))

    try:
        with connection.cursor() as cursor:
            cursor.execute(stmt, variables)
            connection.commit()
    except Exception as e:
        logger.exception(e)
        return False

    return True


def connect(params: dict):
    """Connect to the database"""
    global connection

    try:
        connection = mysql.connector.connect(
            host=params.get("db_host"),
            user=params.get("db_user"),
            password=params.get("db_pass"),
            database=params.get("db_name"),
            autocommit=True
        )
    except Exception as e:
        logger.exception(e)
        exit(1)
