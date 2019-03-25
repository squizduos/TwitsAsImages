#!/usr/bin/python
import sys

import argparse
import logging
import os

import exceptions
import models
from processor import TwitProcessor

CURRENT_PATH = os.getcwd()


def main():
    """
    The main entry point of the application
    """
    logger = logging.getLogger("downloadTwits")
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    # noinspection SpellCheckingInspection
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Reads command line arguments
    parser = argparse.ArgumentParser(description="Download twits as images, and resize it.")
    parser.add_argument("--config-file", nargs="?", default="config.json", help="Application configuration file")
    parser.add_argument("--twits-file", nargs="?", default="",
                        help="Parse JSON files with twits, except of twitter URLs")
    parser.add_argument("--logging", nargs="?", default="INFO", help="Logging level. Default: INFO")
    parser.add_argument("--output-twits-file", nargs="?", default=None,
                        help="JSON file to store results. If not set, results are not written to file.")
    parser.add_argument("--output-file", nargs="?", default=None,
                        help="Name of image file. If several files in config, _1, _2 and etc. suffix added.")
    parser.add_argument("--update", action='store_const', const=True,
                        help="Update twit images, if they are already exist.")
    parser.add_argument("twit", metavar="URL", type=str, nargs='?', default=None, help="Twit URL or JSON twits file")
    command_line_args = parser.parse_args()

    # # Sets application config
    try:
        app_config = models.AppConfig.load_from_file(command_line_args.config_file)
    except FileNotFoundError:
        logger.error(f"No configuration file in {command_line_args.config_file} found.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error while reading application config: {e}")
        sys.exit(1)

    # Sets logging level
    logger.setLevel(command_line_args.logging)
    logger.info(f"Logging level: {command_line_args.logging}")

    if command_line_args.twits_file:
        # Reading twits from file
        logger.info(f"Getting twits from file {command_line_args.twits_file}...")
        try:
            twits = models.Twits.load_from_file(command_line_args.twits_file)
        except exceptions.TwitsConfigValidationError as e:
            logger.info(f"Unable to parse file {command_line_args.twits_file}, errors: {e}.")
            sys.exit(1)
        else:
            logger.info(f"Read {len(twits.twits)} twits from file {command_line_args.twits_file}")
    else:
        logger.info(f"Getting twits from command line...")
        twits = models.Twits()
        twits.twits = list()
        twits.twits.append(
            models.Twit({"url": command_line_args.twit})
        )
        logger.info(f"Read {len(twits.twits)} twits from command line.")

    # Initializing twit processor
    logger.info(f"Initializing twit processor for headless browser {app_config.headless_browser.name}...")
    processor = TwitProcessor(app_config, logger=logger)

    # Detecting saved file template
    if command_line_args.output_file:
        app_config.download.template = command_line_args.output_file
    else:
        app_config.download.template = os.path.join(os.curdir, app_config.download.path, app_config.download.template)
    logger.debug(f"Image file template {app_config.download.template}")

    # Processing twits
    updated_twits = models.Twits()
    updated_twits.twits = list()
    for twit in twits.twits:
        twit_image_exists = bool(twit.get('image', None) and os.path.exists(os.path.join(
            CURRENT_PATH,
            app_config.download.path,
            twit.get('image', None)
        )))
        if twit_image_exists and command_line_args.update != "update":
            logger.info(f"Twit {twit.url} is already exist; skip.")
            updated_twits.twits.append(twit)
        else:
            logger.info(f"Twit {twit.url} processing...")
            updated_twit = processor.process_twit(twit)
            if app_config.get('postprocess', None):
                updated_twit = processor.post_process_twit(updated_twit)
            if twit:
                logger.info(f"Twit {twit.url} is updated successfully and saved to {twit.image}!")
                updated_twits.twits.append(updated_twit)
            else:
                logger.info(f"Twit {twit.url} can't updated. Check logs.")
                updated_twits.twits.append(twit)

    if command_line_args.output_twits_file:
        logger.info(f"Saving twits to {command_line_args.output_twits_file}...")
        updated_twits.save_to_file(command_line_args.output_twits_file)

    logger.info(f"Finished. Thanks.")


if __name__ == "__main__":
    main()
