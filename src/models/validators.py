import os
import re
from schematics.exceptions import ValidationError

import constants


def path_exists(path):
    abspath = os.path.abspath(path)
    if not os.path.exists(abspath):
        raise ValidationError(f"Path {abspath} does not exist")
    return abspath


def file_exists(file_path):
    file_abspath = os.path.abspath(file_path)
    if not os.path.isfile(file_abspath):
        raise ValidationError(f"File {file_abspath} does not exist")
    return file_abspath


def dir_exists(dir_path):
    dir_abspath = os.path.abspath(dir_path)
    if not os.path.isdir(dir_abspath):
        raise ValidationError(f"Directory {dir_abspath} does not exist")
    return dir_abspath


def imagemagick_installed(value):
    error_message = "Image Post-process is activated in config, but ImageMagick is not installed or not found."
    if value is not None:
        try:
            import wand.image
        except ImportError:
            raise ValidationError(error_message)
    return value


def url_belongs_to_tweet(url):
    found = re.search(constants.TWEET_URL_REGEXP, url)
    if not found:
        raise ValidationError(f"Incorrect tweet URL: {url}")
    params = found.groupdict()
    if not "domain" in params or params.get("domain") != "twitter.com":
        raise ValidationError("Incorrect tweet URL")
    return f"https://twitter.com/{params['author']}/{params['id']}"
