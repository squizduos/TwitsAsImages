#!/usr/bin/python
import logging
import os
import random
import string

import exceptions
import models
from helpers.headless_browser import create_browser
from helpers.image_processor import ImageProcessor
from helpers.twitter_embed_api import TwitterEmbedAPI

app_logger = logging.getLogger("downloadTwits")
app_logger.setLevel(logging.INFO)

CURRENT_PATH = os.getcwd()


class TweetProcessor:
    def __init__(self, app_config: models.AppConfig, **kwargs):
        self.app_config = app_config
        self.logger = kwargs.get('logger', app_logger)

        self.browser = self.init_browser(self.app_config.headless_browser)

    def init_browser(self, headless_browser_config: models.HeadlessBrowserConfig):
        try:
            self.logger.debug(f"Creating browser {headless_browser_config.name}.")
            browser = create_browser(headless_browser_config)
            return browser
        except exceptions.HeadlessBrowserException as e:
            self.logger.error(f"{e}")
            return None

    def get_twit_text(self) -> str or None:
        xpath_queries = ["//blockquote/div[2]/p", "//blockquote/p"]
        for xpath_query in xpath_queries:
            twit_text = self.browser.get_element_text(xpath_query)
            if twit_text is not None:
                return twit_text
        return None

    def get_image_file_name(self, url_data: dict) -> str:
        """

        {id} - twit_id
        {author} - twit author
        {random} - random string with 8 digits and letters lowercase
        {no} - no of twit in queue
        :param url_data: URL data about twit (author & id)
        :return:
        """
        filename = self.app_config.download.name

        if "{id}" in filename:
            filename = filename.replace("{id}", url_data['id'])

        if "{author}" in filename:
            filename = filename.replace("{author}", url_data['author'])

        if "{random}" in filename:
            random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
            filename = filename.replace("{random}", random_string)

        if "{no}" in filename:
            directory = os.path.dirname(os.path.join(CURRENT_PATH, self.app_config.download.path, filename))
            filename_beginning, _ = filename.split("{no}")
            no = sum((int(el.startswith(filename_beginning)) for el in os.listdir(directory)))
            filename = filename.replace("{no}", str(no + 1))

        return filename

    def process_twit(self, twit: models.Tweet) -> models.Tweet or None:
        """
        Downloads twit as image and saves it to file

        :param twit: Twit object
        :return: Twit object is not error; else None
        """
        url_data = TwitterEmbedAPI.get_tweet_url_data(twit.url)
        self.logger.debug(f"Getting image file name for {twit.url}...")
        image_filename = self.get_image_file_name(url_data)
        image_path = os.path.join(self.app_config.download.path, image_filename)
        self.logger.debug(f"Getting image file name for twit {twit.url} finished! File name is {image_filename}.")
        self.logger.debug(f"Getting Twitter embed HTML for twit {twit.url}...")
        twit_embed_html = TwitterEmbedAPI.get_tweet_embed_html(
            twit.url,
            self.app_config.twit_embed
        )
        if not twit_embed_html:
            self.logger.error(f"Unable to get twit embed for twit {twit.url}.")
            return None
        self.logger.debug(f"Rendering HTML embed for twit {twit.url}...")
        self.browser.render_html(twit_embed_html)
        self.logger.debug(f"Rendered HTML embed for twit {twit.url} at file {self.browser.current_opened_page}.")
        self.logger.debug(f"Saving twit image for twit {twit.url} to {image_path}...")
        self.browser.take_screenshot(image_path, delay=20)
        self.logger.debug(f"Writing new data to Twit class for twit {twit.url}")
        self.logger.debug(f"Getting text of twit for twit {twit.url}...")
        twit_text = self.get_twit_text()
        self.logger.debug(f"Getting text of twit for twit {twit.url} finished; found text {twit_text}")
        twit.text = twit_text
        twit.image = image_path
        return twit

    def post_process_twit(self, twit: models.Tweet) -> models.Tweet or None:
        """
        Post-process twit image

        :param twit: Twit object
        :return: Twit object if success else None
        """
        if self.app_config.postprocess.trim:
            self.logger.debug(f"Trimming image for twit {twit.url}")
            ImageProcessor.trim_image(twit.image, twit.image)
        if self.app_config.postprocess.resize:
            self.logger.debug(f"Resizing image for twit {twit.url}")
            ImageProcessor.resize_image(
                twit.image,
                twit.image,
                size=self.app_config.postprocess.resize_options
            )
        return twit
