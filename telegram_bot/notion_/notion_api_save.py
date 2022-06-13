import json
import textwrap

from prepare_databases_objects import NOTION_BASES
from telegram_bot.notion_.notion_api import *
from telegram_bot.notion_.utils import extract_url_from_message
from telegram_bot.web_clipper.clipper import WebPage

STUFF, MEDIA, COURSE, PRODUCT, DEVELOPMENT = range(5)


class NotionRecord:

    def __init__(self, message, parent_database) -> None:

        self.message = message
        self.url = extract_url_from_message(self.message)

        self.web_object = self.set_web_object()
        self.is_special_page = self.is_special_page()

        if parent_database is None:
            self.parent_database = self.set_record_parent_database()
        else:
            self.parent_database = parent_database

        self.title = self.set_record_title()
        self.icon = self.set_record_icon_payload()

        self.embedded = self.set_embeddable_content()
        self.embedded_video = self.set_embeddable_video()

        if self.web_object is not None and self.web_object.content is not None:
            self.content = self.web_object.content
        else:
            self.content = ""

        self.children_blocks_paragraphs = self.set_children_blocks()

        self.payload = self.set_record_payload()

        self.created_page_id = None
        self.created_page_url = None

    def set_web_object(self):
        if self.url is not None:
            web_object = WebPage(self.url)
            self.url = web_object.url
            return web_object
        else:
            return None

    def is_special_page(self):
        if self.web_object is not None:
            if self.web_object.special_page is not None:
                return True

        return False

    def set_record_title(self):
        title = self.message if self.url is None else self.web_object.title
        return title

    def set_record_parent_database(self):
        if not self.is_special_page:
            database = NOTION_BASES[NotionDatabase.STUFF_DB]
        else:
            database = NOTION_BASES[self.web_object.special_page.default_database]
        return database

    def set_record_icon_payload(self):
        if (not self.is_special_page) or self.web_object.special_page.default_icon is None:
            icon = {
                "type": "emoji",
                "emoji": self.parent_database.base_default_icon
            }
        else:
            icon = {
                "type": "external",
                "external": {
                    "url": self.web_object.special_page.default_icon
                }
            }
        return icon

    def set_embeddable_content(self):
        # Currently Only Twitter. see docs https://developers.notion.com/reference/block#embed-blocks
        if self.is_special_page and self.web_object.special_page.embeddable_content:
            embedded = {
                "object": "block",
                "type": "embed",
                "embed": {
                    "url": self.url
                }
            }
            return embedded
        else:
            return None

    def set_embeddable_video(self):
        # see docs: https://developers.notion.com/reference/block#video-blocks
        if self.is_special_page and self.web_object.special_page.embeddable_video:
            embedded_video = {
                "object": "block",
                "type": "video",
                "video": {
                    "type": "external",
                    "external": {
                        "url": self.url
                    }
                }
            }
            return embedded_video
        else:
            return None

    def set_children_blocks(self):
        if len(self.content) > 2000:
            content_paragraphs = textwrap.wrap(self.content, 1700, break_long_words=False)
            text = []
            for paragraph in content_paragraphs:
                text.append({
                    "type": "text",
                    "text": {
                        "content": paragraph + " \n ",
                    }
                })
            return text
        else:
            return [
                {
                    "type": "text",
                    "text": {
                        "content": self.content,
                    }
                }
            ]

    def set_record_payload(self):
        parent = {
            'database_id': self.parent_database.id,
        }

        children_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": self.children_blocks_paragraphs
                }
            }
        ]

        if self.embedded is not None:
            children_blocks.append(self.embedded)

        if self.embedded_video is not None:
            children_blocks.insert(0, self.embedded_video)

        icon = self.icon

        properties = {
            "Inbox": {
                'checkbox': True
            },
            "Name": {
                'title': [
                    {
                        'text': {
                            'content': self.title,
                        },
                    },
                ],
            },
            "URL": {
                'url': self.url
            },
            "type": None,
            "platform": None
        }

        if self.is_special_page and self.web_object.special_page.type_select_option is not None:

            if self.parent_database == NOTION_BASES[NotionDatabase.COURSES_DB]:
                properties["Platform"] = {
                    'select':
                        {
                            'name': self.web_object.special_page.type_select_option
                        }

                }

            else:
                properties["type"] = {
                    'multi_select': [
                        {
                            'name': self.web_object.special_page.type_select_option
                        }
                    ]
                }
            print(properties["type"])

        payload = {
            'parent': parent,
            "children": children_blocks,
            'icon': icon,
            'properties': properties,
        }

        if properties["type"] is None or self.parent_database == NOTION_BASES[NotionDatabase.COURSES_DB]:
            payload["properties"].pop("type")

        if properties["platform"] is None or self.parent_database != NOTION_BASES[NotionDatabase.COURSES_DB]:
            payload["properties"].pop("platform")

        return json.dumps(payload)

    def create(self):
        print(self.payload)
        response = NotionEndpoint(method="POST", payload=self.payload, endpoint=NotionEndpoint.CREATE,
                                  resource_id=None).response
        print(response)
        if "id" in response and "url" in response:
            self.created_page_id = response["id"]
            self.created_page_url = response["url"]
            return
        else:
            raise Exception("Failed To Create Page")

    def delete(self):
        payload = json.dumps({
            "archived": True
        })
        response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.PAGE,
                                  resource_id=self.created_page_id).response
        if "url" in response:
            return self.created_page_url
        else:
            raise Exception("Failed To Delete Page")

    def move(self, new_parent_database):
        self.delete()
        self.parent_database = new_parent_database
        self.icon = self.set_record_icon_payload()
        self.payload = self.set_record_payload()
        return self.create()

    def add_topic(self, topic_id):
        payload = json.dumps({

            'properties': {
                "Topic": {
                    'relation': [
                        {
                            'id': topic_id,
                        },
                    ],
                }
            },

        }
        )

        response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.PAGE,
                                  resource_id=self.created_page_id).response
        print(response)
        if "url" in response:
            return
        else:
            raise Exception("Failed To Add Topic")

    def add_project(self, project_id):
        payload = json.dumps({

            'properties': {
                "Project": {
                    'relation': [
                        {
                            'id': project_id,
                        },
                    ],
                }
            },

        }
        )

        response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.PAGE,
                                  resource_id=self.created_page_id).response
        if "url" in response:
            return
        else:
            raise Exception("Failed To Add Project")

    def rename(self, page_new_name):
        self.title = page_new_name
        payload = json.dumps({

            'properties': {
                "Name": {
                    'title': [
                        {
                            'text': {
                                'content': self.title,
                            },
                        },
                    ],
                }
            },

        }
        )

        response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.PAGE,
                                  resource_id=self.created_page_id).response
        if "url" in response:
            return
        else:
            raise Exception("Failed To Rename Page")

    def unbox(self):
        payload = json.dumps({

            'properties': {
                'Inbox': {
                    'checkbox': False
                },
            },

        }
        )
        response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.PAGE,
                                  resource_id=self.created_page_id).response
        if "url" in response:
            return
        else:
            raise Exception("Failed To Unbox Stuff")

    def add_details(self, text):
        self.details = text
        response = NotionEndpoint(method="GET", payload=None, endpoint=NotionEndpoint.PAGE_BLOCKS,
                                  resource_id=self.created_page_id).response

        if "results" in response:
            first_block = response["results"][0]
            block_id = first_block["id"]

            payload = json.dumps({
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": self.details
                            }
                        }
                    ]
                }
            }
            )

            response = NotionEndpoint(method="PATCH", payload=payload, endpoint=NotionEndpoint.BLOCK,
                                      resource_id=block_id).response
            return self.created_page_url
