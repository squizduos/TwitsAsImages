import json
from schematics.exceptions import ValidationError
# noinspection PyProtectedMember
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType

import exceptions


class Twit(Model):
    url = StringType(required=True)
    emoji = StringType(default="")
    image = StringType(default="")
    text = StringType(default="")


class Twits(Model):
    twits = ListType(ModelType(Twit))

    @classmethod
    def load_from_file(cls, json_file: str):
        try:
            with open(json_file, 'r', encoding='utf-8') as twits_file:
                twits = Twits(json.loads("".join(twits_file.readlines())))
        except FileNotFoundError:
            raise exceptions.TwitsConfigValidationError(
                f"File {json_file} is not found."
            )
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {e}."
            )
        try:
            twits.validate()
        except ValidationError as e:
            raise exceptions.TwitsConfigValidationError(
                f"File {json_file} can't validated: errors {e}"
            )
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {e}."
            )
        return twits

    def save_to_file(self, json_file: str) -> bool:
        try:
            self.validate()
        except ValidationError as e:
            raise exceptions.TwitsConfigValidationError(
                f"Twits can't validated before saving: errors {e}"
            )
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {e}."
            )
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.to_primitive(), ensure_ascii=False, indent=4))
        except Exception as e:
            raise exceptions.TwitsConfigValidationError(
                f"Unexpected error {str(e)}."
            )
        return True
