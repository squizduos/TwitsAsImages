import json
import os
from schematics.exceptions import ValidationError
# noinspection PyProtectedMember
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType

import exceptions
from . import validators


class Tweet(Model):
    url = StringType(required=True, validators=[validators.url_belongs_to_tweet])
    emoji = StringType(default="")
    image = StringType(default="")
    text = StringType(default="")


class TweetList(Model):
    tweets = ListType(ModelType(Tweet))

    def load_from_file(self, json_file: str):
        if not os.path.exists(json_file):
            raise exceptions.TweetListValidationError(json_file, custom_message="File not found.")
        try:
            with open(json_file, 'r', encoding='utf-8') as config_file:
                data = json.loads("".join(config_file.readlines()))
                self.tweets = data.get("tweets")
        except ValueError as e:
            raise exceptions.TweetListValidationError(json_file, e, "Not valid JSON file")
        try:
            self.validate()
        except ValidationError as e:
            raise exceptions.TweetListValidationError(json_file, e)

    def save_to_file(self, json_file: str) -> bool:
        try:
            self.validate()
        except ValidationError as e:
            raise exceptions.TweetListValidationError(json_file, e)
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.to_primitive(), ensure_ascii=False, indent=4))
        return True
