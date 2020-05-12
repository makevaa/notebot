from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from datetime import datetime, time


def log(log_message):
    print(str(datetime.now()) + " [NoteBot] " + str(log_message))


#post bot command instructions to user in a message
def post_help(update, context):
    help_text = "ℹ NoteBot /help \n A bot to save your notes to a list. Start a note with a time to have the the bot message you when it's time, eg. /add 18:45 take pizza from oven \n\n Commands: \n /notes - view all notes \n /add my note - add a new note \n /add 18:30 my note - add a note with alarm \n /delete 1 - delete a note (/delete 4 deletes note #4) \n\n"
    update.message.reply_text(help_text)


#add a new note from user's message   
def add_note(update, context):
    msg = update.message.text
    msg = msg.replace('/add', '')
    msg = msg.strip()

    if (len(msg) > 0):
        write_to_file(msg)
        update.message.reply_text('✅ Added note "' + str(msg) + '" /notes')
    else:
        update.message.reply_text("❌ Can't add empty note, specify a note message (eg. /add this is my test note)")


#delete a note from notes.txt, also check if user entered a valid note number
def delete_note(update, context):
    log('delete_note')
    msg = update.message.text
    msg = msg.replace('/delete', '')
    msg = msg.strip() 
    if (len(msg) <= 0):
        update.message.reply_text("❌ Can't delete note; specify note number to delete, eg. /delete 1  /notes")
    elif (int(msg) > get_note_count() or int(msg) < 0):
        update.message.reply_text("❌ Can't delete note; note with that number doesn't exist /notes")
    else:
        delete_note_line(int(msg))
        update.message.reply_text('✅ Deleted note #' + str(msg) + ' /notes')


#delete a note line from the notes.txt
def delete_note_line(line_number):
    line_to_delete = int(line_number) - 1
    notes_file = open('notes.txt', 'r')
    temp_file = open('temp.txt', 'w')
    line = notes_file.readline()    

    #copy notes.txt contents to temp.txt, don't copy the line to be deleted
    i = 0
    while line != '':
        if (i != line_to_delete):
            temp_file.write(line)
        line = notes_file.readline()
        i += 1
    notes_file.close()
    temp_file.close()

    #copy the new list back to notes.txt from temp.txt
    notes_file = open('notes.txt', 'w')
    temp_file = open('temp.txt', 'r')
    line = temp_file.readline()
    while line != '':
        notes_file.write(line)
        line = temp_file.readline()
    notes_file.close()
    temp_file.close()


#read all notes from notes.txt, post to user in a single message
def post_notes(update, context):
    notes_file = open('notes.txt', 'r') 
    notes_string = '📒 Saved notes: \n'
    line = notes_file.readline().strip()
    i = 1
    while line != '':
        notes_string = notes_string + '[' + str(i) + '] ' + line + '\n'    
        line = notes_file.readline().strip()
        i += 1
    notes_file.close()   
    update.message.reply_text(notes_string)


#read notes.txt, count lines and return the note_count
def get_note_count():
    note_count = 0
    notes_file = open('notes.txt', 'r')
    line = notes_file.readline()    
    while line != '':
        note_count += 1
        line = notes_file.readline()
    notes_file.close()
    return note_count

    
def write_to_file(my_string):
    with open('notes.txt', 'a') as notes_file:
        notes_file.write(str(my_string) + '\n')


#get current time using the datetime module
def get_current_time():
    now = datetime.now()
    #build a simple ISO format time string from the datetime object
    hour = now.hour
    minute = now.minute
    second = now.second   
    if(hour < 10): hour = '0' + str(hour)
    if(minute < 10): minute = '0' + str(minute)   
    if(second < 10): second = '0' + str(second) 
    #create a simpler time object from ISO format string for easier comparison later
    new_time_object = time.fromisoformat(str(hour) + ':' + str(minute) + ':'+ str(second))  
    return new_time_object


#read notes to check if they have an alarm time, and if the time has passed, this is polled regularly
def check_for_alarms(context: CallbackContext):
    user_id = YOUR_USER_ID #set your own user id to have the bot send messages to you https://telegram.me/userinfobot
    now = get_current_time()

    #read the notes.txt to check if any notes have an alarm time set
    i = 1
    notes_file = open('notes.txt', 'r')
    line = notes_file.readline()    

    while line != '':
        line_content = line.split() 
        #if the first element in note text includes ":", assume it's from an alarm time (eg. "18:30")
        if ':' in line_content[0]:
            #convert note alarm string to ISO format string, then build a time object from it, 6:30 would be converted to 06:30:00
            note_alarm = line_content[0].split(":")
            hour = int(note_alarm[0])
            minute = int(note_alarm[1])
            second = '00'
            if(hour < 10): hour = '0' + str(hour)
            if(minute < 10): minute = '0' + str(minute)   
    
            note_alarm_time_object = time.fromisoformat(str(hour) + ':' + str(minute) + ':'+ str(second)) #build a time object

            #compare the time objects, send the message to user if it's time
            if (now > note_alarm_time_object):
                alarm_message = "🕑 Automatic note alarm: " + line
                context.bot.send_message(chat_id=user_id, text=alarm_message)
                delete_note_line(i) #delete the note after it has been sent

        i += 1
        line = notes_file.readline()
    notes_file.close()
   

def main():
    updater = Updater('YOUR_TOKEN', use_context=True)
    dp = updater.dispatcher
    log("Started")
    
    dp.add_handler(CommandHandler('help', post_help))
    dp.add_handler(CommandHandler('add', add_note))
    dp.add_handler(CommandHandler('delete', delete_note))
    dp.add_handler(CommandHandler('notes', post_notes))

    j = updater.job_queue
    j.run_repeating(check_for_alarms, interval=10, first=0) #check for alarms every 10 seconds

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()