import html
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from prepare_databases_objects import SPECIAL_WEBPAGES
from telegram_bot.web_clipper.web_browser import Browser


class WebPage:

    def __init__(self, url):

        self.url = url
        self.special_page = self.deduce_special_page_type()
        self.html_soup = self.get_html_soup(
            selenium=True) if self.special_page is not None and self.special_page.selenium else self.get_html_soup()
        self.title = self.get_title()
        self.content = self.get_content()

    def deduce_special_page_type(self):

        if "youtu.be/" in self.url:
            self.url = self.url.replace("youtu.be/", "www.youtube.com/watch?v=")
        webpage_url = self.url.lower()

        for special_webpage in SPECIAL_WEBPAGES:
            if re.search(special_webpage.url_pattern, webpage_url):
                return special_webpage

        return None

    def get_html_soup(self, selenium=False):
        return BeautifulSoup(Browser(self.url, selenium).html, 'html.parser')

    def get_title(self):

        try:
            if self.special_page is not None:
                if self.special_page.title_html_tag is not None:
                    self.title = self.html_soup.find_all(self.special_page.title_html_tag)[0].get_text()
                else:
                    self.title = self.html_soup.title.string

                if self.special_page.title_pattern is not None:
                    self.title = self.title.replace(self.special_page.title_pattern, "")
            else:
                self.title = self.html_soup.title.string


        except Exception:
            if self.special_page is not None:
                self.title = self.special_page.default_title

        if self.title is None:
            self.title = "New Saved URL"
        print(self.title)
        return self.title

    def get_content(self):
        # 4 is youtube
        content = None
        if self.special_page == SPECIAL_WEBPAGES[4]:

            try:
                page_html = Browser(self.url).html.decode('utf_8')
                captions_url = page_html.split("{\"captionTracks\":[{\"baseUrl\":\"")[1].split("\"")[0].replace(
                    "\\u0026", "&")

                if 'lang=' in captions_url:
                    captions_url = captions_url.split('lang=')[0] + 'lang=en'
                    captions_xml_string = Browser(captions_url).html.decode('utf_8')
                    captions_xml_string = html.unescape(captions_xml_string)

                    captions_xml_tree = ET.ElementTree(ET.fromstring(captions_xml_string))
                    root = captions_xml_tree.getroot()
                    captions = ""
                    for child in root:
                        captions += child.text
                        captions += '\n'

                    content = captions
                    print(captions)

            except Exception:
                print('Couldn\'t get youtube script')

        return content
