from telegram import ParseMode

from prepare_databases_objects import NOTION_BASES
from telegram_bot.notion_.notion_api import NotionDatabase
from telegram_bot.notion_.notion_api_retrieve import (
    get_notion_list as any_list)
from telegram_bot.telegram_.telegram_configs import MY_CHAT_ID


def retrieve_lists_handler(update, context):
    if update.message.chat_id == MY_CHAT_ID:
        command = update.message.text

        if command == "/shopping":
            message = "🛍️ *Getting Your Shopping List...*"
            database = NOTION_BASES[NotionDatabase.SHOPPING_DB]

        elif command == "/tv":
            message = "📺 *Getting Some TV Shows Suggestions...*"
            database = NOTION_BASES[NotionDatabase.TV_DB]

        elif command == "/movies":
            message = "📽️ *Getting Some Movies Suggestions...*"
            database = NOTION_BASES[NotionDatabase.MOVIES_DB]

        elif command == "/read":
            message = "📰 *Getting Some Articles to Read...*"
            database = NOTION_BASES[NotionDatabase.MEDIA_DB]
        else:
            return

        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.MARKDOWN)

        result = any_list(database)

        for item in result:

            line = f'🔘 [{item["title"]}]({item["url"]})'
            if database != NOTION_BASES[NotionDatabase.SHOPPING_DB]:
                line += f' | [See Notion]({item["notion_url"]})'

            context.bot.send_message(
                chat_id=update.effective_chat.id, text=line, parse_mode=ParseMode.MARKDOWN)


def retrieve_inbox_handler(update, context):
    if update.message.chat_id == MY_CHAT_ID:
        for message in context.user_data["last_ten_records"]:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.MARKDOWN)
