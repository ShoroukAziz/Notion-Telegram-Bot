import requests

NOTION_HEADERS = {
    'Authorization': "Add your secret key",
    'Content-Type': 'application/json',
    'Notion-Version': '2021-08-16'
}


class NotionEndpoint:
    HEADERS = NOTION_HEADERS
    DOMAIN = 'https://api.notion.com/v1'
    CREATE, QUERY_DB, PAGE, BLOCK, PAGE_BLOCKS = range(5)

    def __init__(self, method, payload, endpoint, resource_id):
        self.method = method
        self.payload = payload
        self.endpoint = endpoint
        self.resource_id = resource_id
        self.url = self.generate_endpoint_url()
        self.response = self.call_api()

    def generate_endpoint_url(self):
        url = ""

        if self.endpoint == NotionEndpoint.QUERY_DB:
            url = f'/databases/{self.resource_id}/query'
        elif self.endpoint == NotionEndpoint.PAGE:
            url = f'/pages/{self.resource_id}'
        elif self.endpoint == NotionEndpoint.CREATE:
            url = '/pages'
        elif self.endpoint == NotionEndpoint.BLOCK:
            url = f'/blocks/{self.resource_id}'
        elif self.endpoint == NotionEndpoint.PAGE_BLOCKS:
            url = f'/blocks/{self.resource_id}/children'

        return NotionEndpoint.DOMAIN + url

    def call_api(self):
        response = requests.request(self.method, self.url, headers=NotionEndpoint.HEADERS, data=self.payload).json()
        # print(self.url)
        # print(response)
        return response


class NotionDatabase:
    STUFF_DB, TASKS_DB, SHOPPING_DB, PROJECTS_DB, EVENTS_DB, \
    NOTES_DB, MEDIA_DB, SOFTWARE_DB, FACEBOOK_DB, MOVIES_DB, \
    TV_DB, BOOKS_DB, COURSES_DB, TOPICS_DB, QUOTES_DB, \
    RECIPES_DB, WISHLIST_DB, STORES_DB, WELLNESS_DB, TRAVEL_DB, \
    ATTRACTIONS_DB, ACTEVITIES_DB, DEVRES_DB = range(23)

    def __init__(self, name, base_id, base_default_icon, retrieve_filters=None, tag=None, has_topic=False):
        self.name = name
        self.id = base_id
        self.base_default_icon = base_default_icon
        self.retrieve_filters = retrieve_filters
        self.tag = tag
        self.has_topic = has_topic
