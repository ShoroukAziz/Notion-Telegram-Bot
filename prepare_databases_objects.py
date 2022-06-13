import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

import sqlite3

from telegram_bot.notion_.notion_api import NotionDatabase
from telegram_bot.notion_.notion_api_retrieve import get_notion_list
from telegram_bot.web_clipper.special_page import SpecialPage


def start():
    conn = sqlite3.connect("notion.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT * FROM bases")
    rows = cur.fetchall()

    notion_bases = {}
    special_webpages = []

    for row in rows:
        # print(row)
        key = row[0]
        if row[3] is not None:
            filters = row[3].replace("'", '"')
            notion_bases[key] = NotionDatabase(name=row[2].strip(),
                                               base_id=row[1].strip(),
                                               base_default_icon=row[4].strip(),
                                               retrieve_filters=filters.strip(),
                                               tag=row[5],
                                               has_topic=row[6])
        else:
            notion_bases[key] = NotionDatabase(name=row[2].strip(),
                                               base_id=row[1].strip(),
                                               base_default_icon=row[4].strip(),
                                               retrieve_filters=None,
                                               tag=row[5],
                                               has_topic=row[6])

    cur.execute("SELECT * FROM special_webpages")
    rows = cur.fetchall()

    special_webpages = []
    for row in rows:
        special_webpages.append(
            SpecialPage(type_id=row[0],
                        default_database=row[1],
                        default_title=row[2],
                        url_pattern=row[3],
                        default_icon=row[4],
                        selenium=row[5],
                        type_select_option=row[6],
                        embeddable_content=row[7],
                        embeddable_video=row[8],
                        title_pattern=row[9],
                        title_html_tag=row[10]
                        ))

    return notion_bases, special_webpages


NOTION_BASES, SPECIAL_WEBPAGES = start()
HOT_TOPICS = get_notion_list(NOTION_BASES[NotionDatabase.TOPICS_DB])
ACTIVE_PROJECTS = get_notion_list(NOTION_BASES[NotionDatabase.PROJECTS_DB])
