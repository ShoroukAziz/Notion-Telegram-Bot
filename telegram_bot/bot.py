import logging
import os

from telegram.ext import (Updater, CommandHandler)

from telegram_bot.telegram_.retrieve_bot import retrieve_lists_handler, retrieve_inbox_handler
from telegram_bot.telegram_.save_and_edit_bot import save_edit_conv_handler
from telegram_bot.telegram_.telegram_configs import TOKEN

PORT = int(os.environ.get('PORT', 8080))

# heroku configs
APP_NAME = 'add your heroku app name'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def run_local(updater):
    updater.start_polling()


def run_remote(updater):
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=APP_NAME + TOKEN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # dispatcher.add_error_handler(error)
    dispatcher.add_handler(CommandHandler(
        ("tv", "movies", "shopping", "read"), retrieve_lists_handler))

    dispatcher.add_handler(CommandHandler(
        "inbox", retrieve_inbox_handler))

    dispatcher.add_handler(save_edit_conv_handler)

    # run_local(updater)

    run_remote(updater)
    updater.idle()


if __name__ == '__main__':
    main()
