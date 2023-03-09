REGEX_NAME = "^[a-zA-Z ]{1,100}$"
REGEX_TITLE = "^[A-Z0-9]{3,4}$"
REGEX_DEPARTMENT = "^[a-zA-Z0-9 ]{2,5}$"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

WORKBOOK_NAME = "Attendance_%b%Y"
SHEET_NAME = "%d%b"
SHEET_ROWS = 250
SHEET_COLUMNS = 4

SELECT_ACTIVE_USERS = "SELECT userId, title, name, department, NULL AS status FROM users WHERE accStatus = 1"
