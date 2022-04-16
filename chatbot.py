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
import os
import pymysql
from pymysql import converters
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


conv = converters.conversions
conv[246] = float
db = pymysql.connect(host=(os.environ['HOST']),user=(os.environ['USER']),password=(os.environ['PASSWORD']), database=(os.environ['DB']), conv=conv)

mountain_set = {'Lion', 'TungYeung', 'Lantau'}
#choose_mountain = ''
     

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
        'Difficulty: /easy or /medium or /hard.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    return SEARCH

def search(update: Update, context: CallbackContext) -> int:
    print("--------search--------")
    input = update.message.text
    print("input: " + input)
    difficulty = input.lstrip('/')
    
    #mysql get name
    
    difficulty = "'" + difficulty + "'"
    sql = f"SELECT name FROM mountain WHERE difficulty = {difficulty}"
    global db
    cursor = db.cursor()
    result_list = []
    try:
        cursor.execute(sql)

        results = cursor.fetchall()
    
        for i in results:       
            str = ''.join(i)
            result_list.append(str)

    except:
        db.rollback()

    
    text = ''
    for i in result_list:
        text += '/' + i + '\n\n'
    print(text)

    update.message.reply_text(
        'Mountains:\n\n'
        + text +
        'click one to get the location.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    print("--------location--------")
    input = update.message.text
    print("input:" + input)
    
    global mountain_set
    
    longitude = 114.326784
    latitude = 22.345672
    
    #global choose_mountain 
    choose_mountain = input.lstrip('/')
    if (choose_mountain not in mountain_set):
        update.message.reply_text('Send the mountain name.')        
        return LOCATION

    choose_mountain = "'" + choose_mountain + "'"
    #mysql get location

    sql = f"SELECT longitude, latitude FROM mountain WHERE name = {choose_mountain}"

    global db
    cursor = db.cursor()
    location = ()
    
    try:
        print("query location")
        cursor.execute(sql)
        print('success')

        results = cursor.fetchall()
        print(results) 
        location = results[0]
        longitude = location[0]
        latitude = location[1]
        
    except:
        print("rollback happen")
        db.rollback()

    

    print(longitude)
    print(latitude)

    update.message.reply_text(
        'The location of this mountain is:'
    )
    update.message.reply_location(longitude=longitude, latitude=latitude)
    
    update.message.reply_text(
        'I got a picture for you!\n\n' 
        'Send ' + input + ' to see it.\n\n'
    )
    

    
    return PHOTO


def skip_location(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        'I got a picture for you!\n\n' 
        'Send ' + input + ' to see it.\n\n'
    )

    return PHOTO




def photo(update: Update, context: CallbackContext) -> int:
    print("--------photo--------")

    input = update.message.text
    print("input: " + input)
    
    #global choose_mountain 
    #if choose_mountain != input.lstrip('/'):
    #    return PHOTO
    
    choose_mountain = input.lstrip('/')
    choose_mountain = "'" + choose_mountain + "'"
    #PHOTO_PATH = './picture' + input + '.jpg'
    
    global db
    cursor = db.cursor()
    #mysql get photo_url
    sql = f"SELECT picture FROM mountain WHERE name = {choose_mountain}"


    try:
        print('query photo_url')
        cursor.execute(sql)
        print('success')
        results = cursor.fetchall()
        results = results[0]
        list = []
        for i in results:       
            str = ''.join(i)
            list.append(str)
        PHOTO_PATH = list[0]
        print(PHOTO_PATH)
        
    except:
        db.rollback()

    update.message.reply_text('This is the picture.\n\n')
    update.message.reply_photo(photo=open(PHOTO_PATH, 'rb'))
    update.message.reply_text(
        'I have a recommended route for you!\n\n'
        'Send /route to see it.'
    )
    
    
    return ROUTE


def skip_photo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Enjoy your hiking!')

    return ROUTE


def route(update: Update, context: CallbackContext) -> int:
    print("------route---------")
    #mysql get route
    #route = 'A>B>C>D'
    
    update.message.reply_html('https://www.skyscanner.com.hk/news/7-hong-kong-hiking-routes')
    update.message.reply_text('Enjoy your hiking!')

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
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)

    

    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states SEARCH, LOCATION, PHOTO, and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE: [MessageHandler(Filters.all, choose)],
            SEARCH: [MessageHandler(Filters.regex('^(/easy|/medium|/hard)$'), search)],
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
