# NoteBot
Python based Telegram bot to save notes and send timed alarms from them. Notes are saved and read from a local text file. 
If a note has a valid alarm time, bot will send a message to the user at the specified time. 
Note is deleted after the alarm message has been sent.

## Commands & instructions
- /notes - view all notes
- /add my note - add a new note without an alarm
- /add 18:30 my note - enter a time to add a note with a timed alarm
- /delete 1 - delete a note specified by the number, eg. /delete 4 deletes note #4
- /help - post help message

