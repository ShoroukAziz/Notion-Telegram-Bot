import re


def extract_url_from_message(message):
    is_url = re.search("(?P<url>https?://[^\s]+)", message)
    if is_url is None:
        url = None
    else:
        url = is_url.group("url")
    return url
