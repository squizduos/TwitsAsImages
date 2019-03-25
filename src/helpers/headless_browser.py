import time

import os
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import exceptions
import models

CURRENT_PATH = os.getcwd()


class HeadlessBrowser:
    def __init__(self, **options: dict):
        """

        :param logger: Application logger
        :param browser_type: Browser type
        :param options: Browser options
        """
        self.browser = None
        self.current_opened_page = None
        self.options = options

    def render_html(self, embed_html: str) -> bool:
        """
        Renders sample web page with embedded HTML and opens it in browser.

        :param embed_html: string with embed HTML
        :return: True if operation is successful; False otherwise
        """
        operation_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
        html_filename = f"/tmp/{operation_id}.html"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), 'r') as template_file:
            page_template = "".join(template_file.readlines())
            try:
                with open(html_filename, "w", encoding='utf-8') as f:
                    html_content = page_template.replace("{% embed %}", embed_html)
                    f.writelines(html_content)
            except Exception as e:
                raise exceptions.HeadlessBrowserException(f"Can't create file {html_filename} because of error: {e}.")
            try:
                self.browser.get(f"file://{html_filename}")
            except Exception as e:
                raise exceptions.HeadlessBrowserException(f"Can't open web page {html_filename} because of error: {e}.")
            else:
                self.current_opened_page = html_filename
                return True

    def take_screenshot(self, image_filename: str, delay: int = 0) -> bool:
        """
        Takes screenshot after delay and saves it to file.

        :param image_filename: image file path
        :param delay: delay before screenshot (in sec)
        :return: True, if operation is successful; False otherwise
        """
        time.sleep(delay)
        self.browser.save_screenshot(image_filename)
        # os.remove(self.current_opened_page)
        return True

    def get_element_text(self, xpath: str) -> str or None:
        """
        Find text by xpath and returns it. Returns None if not found.

        :param xpath: XPath of element with text
        :return: Element text or None
        """
        try:
            twit_text = self.browser.find_element_by_xpath(xpath).text
        except:
            return None
        return twit_text


class PhantomJSBrowser(HeadlessBrowser):
    def __init__(self, **options):
        super().__init__(**options)

        executable_path = os.path.join(CURRENT_PATH, options.get('executable_path'))

        self.browser = webdriver.PhantomJS(
            executable_path=executable_path,
            service_log_path="/dev/null"
        )


class ChromeBrowser(HeadlessBrowser):
    def __init__(self, **options):
        super().__init__(**options)

        executable_path = os.path.join(CURRENT_PATH, options.get('executable_path'))

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--hide-scrollbars")

        self.browser = webdriver.Chrome(
            executable_path,
            chrome_options=chrome_options,
            service_log_path="/dev/null"
        )


def create_browser(options: models.HeadlessBrowserConfig):
    if options.name == 'phantomjs':
        return PhantomJSBrowser(**options.to_primitive())
    elif options.name == 'chrome':
        return ChromeBrowser(**options.to_primitive())
    else:
        raise exceptions.HeadlessBrowserException("Browser is not supported.")
