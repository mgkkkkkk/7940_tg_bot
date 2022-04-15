#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import pymysql
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSE, SEARCH, LOCATION, PHOTO, ROUTE = range(5)

#bot = telegram.Bot(token="5211434946:AAEv-3PvEJ98N1ufat_t96KDgUyyuzl3KZY"

db = pymysql.connect(host='192.168.95.100',user='root',password='123456',database='comp7940')

mountain_set = {'Lion', 'TungYeung'}
choose_mountain = ''
     

def start(update: Update, context: CallbackContext) -> int:
    print(update.message.from_user.name)
    reply_keyboard = [['Hiking', 'Quit']]

    update.message.reply_text(
        'Hi! What do you want?\n\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Do what?'
        ),
    )

    return CHOOSE


def choose(update: Update, context: CallbackContext) -> int:
    
    if (update.message.text == 'Quit'):
        return ConversationHandler.END
    
    update.message.reply_text(
        'Search a mountain: \n\n'
        'Difficulty: /easy or /midium or /hard.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    return SEARCH

def search(update: Update, context: CallbackContext) -> int:
    difficulty = update.message.text
    
    
    #mysql get name
    global db
    cursor = db.cursor()
    sql = "SELECT name FROM mountain WHERE difficulty = " + difficulty
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()
    
    a = 'Lion'
    update.message.reply_text(
        'There are the mountains:\n\n'
        '/' + a + '\n\n'
        'click one to get the location.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    
    input = update.message.text
    global mountain_set
    global choose_mountain 
    choose_mountain = input.lstrip('/')
    if (choose_mountain not in mountain_set):
        update.message.reply_text('Send the mountain name.')        
        return LOCATION

    
    #mysql get location
    longitude = 114.326784
    latitude = 22.345672
    update.message.reply_text(
        'The location of this mountain is:'
    )
    update.message.reply_location(longitude=longitude, latitude=latitude)
    
    update.message.reply_text(
        'I got a picture for you!\n\n' 
        'Send ' + input + ' to see it.\n\n'
    )
    
    #bot.send_location(chat_id=user.id, longitude=114.000000, latitude=22.000000)
    
    return PHOTO


def skip_location(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        'I got a picture for you!\n\n' 
        'Send ' + input + ' to see it.\n\n'
    )

    return PHOTO




def photo(update: Update, context: CallbackContext) -> int:

    input = update.message.text
    print(input)
    global choose_mountain 
    if choose_mountain != input.lstrip('/'):
    
        return PHOTO
    
    #global dbconn
    #mysql get photo_url

    PHOTO_PATH = './picture' + input + '.jpg'

    update.message.reply_text('This is the picture.\n\n')
    update.message.reply_photo(photo=open(PHOTO_PATH, 'rb'))
    update.message.reply_text(
        'I have a recommended route for you!\n\n'
        'Send /route to see it.'
    )
    
    #bot = telegram.Bot(token="5211434946:AAEv-3PvEJ98N1ufat_t96KDgUyyuzl3KZY")
    #bot.send_photo(chat_id=user.id, photo=open(PHOTO_PATH, 'rb'))
    
    return ROUTE


def skip_photo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Enjoy your hiking!')

    return ROUTE


def route(update: Update, context: CallbackContext) -> int:
    
    #mysql get route
    route = 'A>B>C>D'
    update.message.reply_text(
        'Route: ' + route + '\n\n'
        'Enjoy your hiking!'
    )

    return ConversationHandler.END


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('I provide information about hiking!')

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5211434946:AAEv-3PvEJ98N1ufat_t96KDgUyyuzl3KZY")

    

    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states SEARCH, LOCATION, PHOTO, and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE: [MessageHandler(Filters.all, choose)],
            SEARCH: [MessageHandler(Filters.regex('^(/easy|/midium|/hard)$'), search)],
            LOCATION: [MessageHandler(Filters.all, location)],
            PHOTO: [MessageHandler(Filters.all, photo)],
            ROUTE: [MessageHandler(Filters.regex('^(/route)$'), route)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
