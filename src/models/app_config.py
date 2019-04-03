import json
import os
from schematics.exceptions import ValidationError
# noinspection PyProtectedMember
from schematics.models import Model
from schematics.types import StringType, DictType, ModelType, BooleanType, IntType

import constants
import exceptions
from . import validators


class HeadlessBrowserConfig(Model):
    name = StringType(required=True, choices=constants.SUPPORTED_HEADLESS_BROWSERS)
    executable_path = StringType(required=True, validators=[validators.file_exists])


class TweetEmbedConfig(Model):
    maxwidth = IntType(default=325, **constants.SUPPORTED_EMBED_TWEET_MAXSIZE)
    hide_media = BooleanType(default=False)
    hide_thread = BooleanType(default=False)
    omit_script = BooleanType(default=False)
    align = StringType(choices=constants.SUPPORTED_EMBED_TWEET_ALIGNS, default='None')
    related = StringType()
    lang = StringType(choices=constants.SUPPORTED_EMBED_TWEET_LANGUAGES, default="en")
    theme = StringType(choices=constants.SUPPORTED_EMBED_TWEET_THEMES)
    link_color = StringType()
    widget_type = StringType(choices=constants.SUPPORTED_EMBED_TWEET_WIDGET_TYPES, default="")
    dht = BooleanType(default=False)


class DownloadConfig(Model):
    path = StringType(required=True, validators=[validators.dir_exists])
    name = StringType(default="{id}.png")
    update = BooleanType(default=False)


class PostProcessConfig(Model):
    resize = BooleanType(default=False)
    trim = BooleanType(default=False)
    resize_options = DictType(StringType)


class AppConfig(Model):
    headless_browser = ModelType(HeadlessBrowserConfig, required=True)
    twit_embed = DictType(StringType)
    download = ModelType(DownloadConfig, required=True)
    postprocess = ModelType(PostProcessConfig, validators=[validators.imagemagick_installed])

    @classmethod
    def load_from_file(cls, json_file: str):
        if not os.path.exists(json_file):
            raise exceptions.AppConfigValidationError(json_file, custom_message="File not found.")
        try:
            with open(json_file, 'r', encoding='utf-8') as config_file:
                config = cls(json.loads("".join(config_file.readlines())))
        except ValueError as e:
            raise exceptions.AppConfigValidationError(json_file, e, "Not valid JSON file")
        try:
            config.validate()
        except ValidationError as e:
            raise exceptions.AppConfigValidationError(json_file, e)
        return config
