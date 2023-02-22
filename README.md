# Attendance Reporter Telegram Bot
A small project to learn how to make a Telegram bot, along with integration with Google Drive excel spreadsheets.

## Main target features

- User registration (DONE)
- User registration approval by superiors (DONE)
- Write to spreadsheet
- Update spreadsheet at regular intervals
- Upload spreadsheet to Google Drive

## More features
- Allow user to update particulars
- Allow user to update attendance status
- Allow superiors to remove users under their wing
- Allow users to pull attendance list
- Allow users to download attendance list
- ...

## Database table

| userId | chatId | name | title | department | role | accStatus |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| 11112222 | 1112222 | John Doe | EXEC | IT | User | 0 |

role:
- User
- Admin

accStatus: 
- 0: Pending approval
- 1: Approved
- 2: Rejected

## License

MIT
