import math

from telegram import (
    InlineKeyboardMarkup, InlineKeyboardButton, ParseMode)

from prepare_databases_objects import NOTION_BASES
from telegram_bot.notion_.notion_api import NotionDatabase


def prepare_operations_keyboard(topic=False, project=False):
    buttons = [
        [
            InlineKeyboardButton(
                text="✏️ Rename", callback_data="Rename"),
            InlineKeyboardButton(
                text="➡️ Move", callback_data="Move"),
            InlineKeyboardButton(
                text="📝 Add Details", callback_data="Details"),

        ], [

            InlineKeyboardButton(
                text="📤 Unbox", callback_data="Unbox"),
            InlineKeyboardButton(
                text="🗑️ Delete", callback_data="Delete"),
            InlineKeyboardButton(
                text="✅ Done", callback_data="End"), ],

    ]

    if topic:
        buttons.append([InlineKeyboardButton(
            text='Add Topic', callback_data="Topic")])

    if project:
        buttons.append([InlineKeyboardButton(
            text='Add Project', callback_data="Project")])

    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


def prepare_keyboard_from_list(no_of_keys_in_row=1, source_list=[], keyboard_bases=True):
    buttons = []
    bases_len = len(source_list)
    rows = math.ceil(bases_len / no_of_keys_in_row)
    items_counter = 0
    for rows_counter in range(rows):
        buttons_in_row_counter = 0
        row = []
        while buttons_in_row_counter <= no_of_keys_in_row - 1 and items_counter < bases_len:
            item = source_list[items_counter]
            if keyboard_bases:
                row.append(InlineKeyboardButton(text=item.name, callback_data=items_counter))
            else:
                row.append(InlineKeyboardButton(text=item["title"], callback_data=item["id"]))

            buttons_in_row_counter += 1
            items_counter += 1
        buttons.append(row)
        rows_counter += 1

    buttons.append([InlineKeyboardButton(
        text='🔙 Back', callback_data="Back")])

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


def display_operations_keyboard_with_message(update, context, bot_message):
    if context.user_data["record"].parent_database.has_topic:
        keyboard = prepare_operations_keyboard(topic=True)
    elif context.user_data["record"].parent_database == NOTION_BASES[NotionDatabase.TASKS_DB]:
        keyboard = prepare_operations_keyboard(project=True)
    else:
        keyboard = prepare_operations_keyboard()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=bot_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
