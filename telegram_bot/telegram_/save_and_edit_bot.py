from telegram import (Update)
from telegram.ext import (CommandHandler, CallbackContext, MessageHandler,
                          Filters, ConversationHandler, CallbackQueryHandler)

from prepare_databases_objects import HOT_TOPICS, ACTIVE_PROJECTS
from telegram_bot.notion_.notion_api_retrieve import search_notion_database
from telegram_bot.notion_.notion_api_save import NotionRecord
from telegram_bot.telegram_.keyboards import *
from telegram_bot.telegram_.telegram_configs import MY_CHAT_ID

SAVE, SELECT_OPERATION, RENAME, MOVE, DETAILS, TOPIC, PROJECT = range(7)

storage = []


def save(update, context):
    if update.message.chat_id == MY_CHAT_ID:
        # Create a record in The Stuff database by default from the incoming message

        record = None
        topic_search = None

        for i in NOTION_BASES:
            if NOTION_BASES[i].tag is not None and NOTION_BASES[i].tag != "" and update.message.text.startswith(
                    NOTION_BASES[i].tag):
                input_message = update.message.text.split(NOTION_BASES[i].tag)[1]
                if '#' in input_message:
                    all_input = input_message.split('#')
                    topic_search = all_input[1]
                    record = NotionRecord(all_input[0], NOTION_BASES[i])
                else:
                    record = NotionRecord(input_message, NOTION_BASES[i])
                break

        if record is None:
            input_message = update.message.text
            if '#' in input_message:
                all_input = input_message.split('#')
                topic_search = all_input[1]
                record = NotionRecord(all_input[0], None)
            else:
                record = NotionRecord(input_message, None)

        record.create()

        context.user_data["record"] = record

        bot_message = f"*{record.title}* added to *{record.parent_database.name} base*." \
                      f" [Find it here]({record.created_page_url})"

        if len(storage) == 10:
            storage.pop(0)
        storage.append(bot_message)
        context.user_data["last_ten_records"] = storage

        if topic_search is None:
            display_operations_keyboard_with_message(update, context, bot_message)
            return SELECT_OPERATION

        else:
            search_result = search_notion_database(NOTION_BASES[NotionDatabase.TOPICS_DB], topic_search)
            keyboard = prepare_keyboard_from_list(no_of_keys_in_row=1, source_list=search_result, keyboard_bases=False)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='What Topic?', parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
            return TOPIC


def operation_selector(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    record = context.user_data["record"]

    if query.data == "Rename":
        query.edit_message_text(
            text="Enter a new Name or /keepName")
        return RENAME

    elif query.data == "Delete":

        record.delete()
        deletion_message = f"[Deleted page]({record.created_page_url})"
        query.edit_message_text(
            text=deletion_message, parse_mode=ParseMode.MARKDOWN)

        storage.pop()
        context.user_data["last_ten_records"] = storage

        return SAVE

    elif query.data == "Unbox":
        record = context.user_data["record"]
        record.unbox()
        bot_message = f"[Page out of Inbox]({record.created_page_url})"
        display_operations_keyboard_with_message(update, context, bot_message)
        return

    elif query.data == "Details":
        query.edit_message_text(
            text="Add details to your stuff or /GoBack")
        return DETAILS

    elif query.data == "Move":

        keyboard = prepare_keyboard_from_list(no_of_keys_in_row=4, source_list=NOTION_BASES, keyboard_bases=True)
        update.callback_query.edit_message_text(
            "Where to?", reply_markup=keyboard)
        return MOVE

    elif query.data == "Topic":

        keyboard = prepare_keyboard_from_list(no_of_keys_in_row=1, source_list=HOT_TOPICS, keyboard_bases=False)
        update.callback_query.edit_message_text(
            "Which topic?", reply_markup=keyboard)
        return TOPIC

    elif query.data == "Project":

        keyboard = prepare_keyboard_from_list(no_of_keys_in_row=1, source_list=ACTIVE_PROJECTS, keyboard_bases=False)
        update.callback_query.edit_message_text(
            "Which Project?", reply_markup=keyboard)
        return PROJECT

    else:
        query.message.delete()
        return SAVE


def move(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "Back":
        # query.message.delete()
        bot_message = "Anything else?"

    else:
        record = context.user_data["record"]
        new_base = int(query.data)
        record.move(NOTION_BASES[new_base])
        bot_message = f"*{record.title}* moved to *{record.parent_database.name} base*. [Find it here]({record.created_page_url})"
        storage.pop()
        storage.append(
            f"*{record.title}* added to *{record.parent_database.name} base*.[Find it here]({record.created_page_url})")
        context.user_data["last_ten_records"] = storage

    query.message.delete()
    display_operations_keyboard_with_message(update, context, bot_message)

    return SELECT_OPERATION


def topic(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "Back":
        bot_message = "Anything else?"

    else:
        record = context.user_data["record"]
        topic_id = query.data
        record.add_topic(topic_id)
        bot_message = f"*{record.title}* tagged . [Find it here]({record.created_page_url})"

    query.message.delete()
    display_operations_keyboard_with_message(update, context, bot_message)

    return SELECT_OPERATION


def project(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "Back":
        bot_message = "Anything else?"

    else:
        record = context.user_data["record"]
        project_id = query.data
        record.add_project(project_id)
        bot_message = f"project added to *{record.title}* . [Find it here]({record.created_page_url})"

    query.message.delete()
    display_operations_keyboard_with_message(update, context, bot_message)

    return SELECT_OPERATION


def rename(update, context):
    new_name = update.message.text

    if new_name == "/keepName":
        bot_message = "Ok I'll keep its name. Anything else?"
    else:
        record = context.user_data["record"]
        record.rename(new_name)
        bot_message = f"Renamed it to *{record.title}*. [Find it here]({record.created_page_url})."

        storage.pop()
        storage.append(
            f"*{record.title}* added to *{record.parent_database.name} base*. [Find it here]({record.created_page_url})")
        context.user_data["last_ten_records"] = storage

    display_operations_keyboard_with_message(update, context, bot_message)
    return SELECT_OPERATION


def add_details(update, context):
    text = update.message.text

    if text == "/GoBack":
        bot_message = "Ok. Anything else?"

    else:
        record = context.user_data["record"]
        record.add_details(text)
        bot_message = f"Added the Details.[Find it here]({record.created_page_url}"

    display_operations_keyboard_with_message(update, context, bot_message)
    return SELECT_OPERATION


save_edit_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, save)],
    states={
        SAVE: [MessageHandler(Filters.text, save)],
        SELECT_OPERATION: [CallbackQueryHandler(operation_selector), MessageHandler(Filters.text, save)],
        RENAME: [MessageHandler(Filters.text, rename)],
        MOVE: [CallbackQueryHandler(move), MessageHandler(Filters.text, save)],
        DETAILS: [MessageHandler(Filters.text, add_details)],
        TOPIC: [CallbackQueryHandler(topic), MessageHandler(Filters.text, save)],
        PROJECT: [CallbackQueryHandler(project), MessageHandler(Filters.text, save)]
    },
    fallbacks=[CommandHandler('cancel', SAVE)],
)
