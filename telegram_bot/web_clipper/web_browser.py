import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class Browser:

    def __init__(self, url, selenium=False) -> None:
        self.url = url

        if selenium:
            self.html = self.get_driver()
        else:
            self.html = self.get_request()

    def get_request(self):
        html = requests.get(self.url).content
        return html

    def get_driver(self):
        g_chrome_options = webdriver.ChromeOptions()
        g_chrome_options.add_argument("window-size=1920x1480")
        g_chrome_options.add_argument("disable-dev-shm-usage")
        g_driver = webdriver.Chrome(
            chrome_options=g_chrome_options, executable_path=ChromeDriverManager().install()
        )

        g_driver.get(self.url)

        # time.sleep(1)
        # g_driver.save_screenshot("my_screenshot.png")

        html = g_driver.page_source
        g_driver.close()

        return html
