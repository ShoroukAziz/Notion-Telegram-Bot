import json

from telegram_bot.notion_.notion_api import *


def get_notion_list(database):
    payload = database.retrieve_filters
    print(payload)

    response = NotionEndpoint(method="POST", payload=payload, endpoint=NotionEndpoint.QUERY_DB,
                              resource_id=database.id).response

    print(response)
    notion_list = response["results"]
    return extract(notion_list, database)


def search_notion_database(database, search_text):
    payload = json.dumps({"filter": {"property": "Name", "rich_text": {"contains": search_text}}})
    print(payload)
    response = NotionEndpoint(method="POST", payload=payload, endpoint=NotionEndpoint.QUERY_DB,
                              resource_id=database.id).response
    print(response)
    notion_list = response["results"]
    return extract(notion_list, database)


def extract(notion_list, database):
    records = []

    for item in notion_list:
        title = item["properties"]["Name"]["title"][0]["text"]["content"]
        if "URL" in item["properties"]:
            url = item["properties"]["URL"]["url"]
        else:
            url = ""
        notion_url = "https://notion.com/" + item["id"].replace('-', '')
        page_id = item["id"]
        record = {"title": title,
                  "url": url,
                  "notion_url": notion_url,
                  "id": page_id}
        records.append(record)

    return records
