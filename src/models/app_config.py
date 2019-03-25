import json
from schematics.exceptions import ValidationError
# noinspection PyProtectedMember
from schematics.models import Model
from schematics.types import StringType, DictType, ModelType, BooleanType

import exceptions


class HeadlessBrowserConfig(Model):
    name = StringType(required=True)
    executable_path = StringType(required=True)

    SUPPORTED_BROWSERS = ['phantomjs', 'chrome']

    def validate_name(self, data, value):
        if value not in self.SUPPORTED_BROWSERS:
            supported_str = ", ".join(self.SUPPORTED_BROWSERS)
            raise ValidationError(
                f"Browser {value} is not supported; supported browsers are {supported_str}, data: {data}"
            )
        return value


class DownloadConfig(Model):
    path = StringType(required=True)
    template = StringType(default="{id}.png")


class PostProcessConfig(Model):
    resize = BooleanType(default=False)
    resize_options = DictType(StringType)
    trim = BooleanType(default=False)


class AppConfig(Model):
    headless_browser = ModelType(HeadlessBrowserConfig, required=True)
    twit_embed = DictType(StringType)
    download = ModelType(DownloadConfig, required=True)
    postprocess = ModelType(PostProcessConfig)

    @classmethod
    def load_from_file(cls, json_file: str):
        try:
            with open(json_file, 'r', encoding='utf-8') as config_file:
                config = cls(json.loads("".join(config_file.readlines())))
        except FileNotFoundError as e:
            raise exceptions.TwitsConfigValidationError(
                f"File {json_file} does not found; original error: {e}"
            )
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {e}."
            )
        try:
            config.validate()
        except ValidationError as e:
            raise exceptions.TwitsConfigValidationError(
                f"File {json_file} can't validated: errors {e}"
            )
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {e}."
            )
        return config
