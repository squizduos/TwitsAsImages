#!/usr/bin/python
import sys

import click
import logging
import os
from schematics.exceptions import DataError

import exceptions
import models
from helpers.twitter_embed_api import TwitterEmbedAPI
from processor import TweetProcessor

CURRENT_PATH = os.getcwd()

logger = logging.getLogger("downloadTwits")
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
# noinspection SpellCheckingInspection
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def prepare_config(config_file: str, destination: str or None, filename: str or None, update: bool = False):
    try:
        app_config = models.AppConfig.load_from_file(config_file)
    except exceptions.AppConfigValidationError as e:
        logger.error(e)
        sys.exit(1)
    app_config.download.path = destination if destination else app_config.download.path
    app_config.download.name = filename if filename else app_config.download.name
    app_config.download.update = update
    try:
        app_config.validate()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    return app_config


def process_tweets(config: models.AppConfig, tweets_list: models.TweetList) -> models.TweetList:
    logger.debug(f"Initializing tweet processor for headless browser {config.headless_browser.name}...")
    processor = TweetProcessor(config, logger=logger)

    updated_tweets = models.TweetList()
    updated_tweets.tweets = list()
    for tweet in tweets_list.tweets:
        if tweet.get('image', None):
            twit_image_path = os.path.join(CURRENT_PATH, config.download.path, tweet.get('image'))
            twit_image_exists = os.path.exists(twit_image_path)
        else:
            twit_image_exists = False
        if twit_image_exists and not config.download.update:
            logger.info(f"Tweet {tweet.url} is already exist; skip.")
            updated_tweets.tweets.append(tweet)
        else:
            logger.info(f"Tweet {tweet.url} processing...")
            updated_twit = processor.process_twit(tweet)
            if config.get('postprocess', None):
                updated_twit = processor.post_process_twit(updated_twit)
            if tweet:
                logger.info(f"Tweet {tweet.url} is updated successfully and saved to {tweet.image}!")
                updated_tweets.tweets.append(updated_twit)
            else:
                logger.info(f"Tweet {tweet.url} can't updated. Check logs.")
                updated_tweets.tweets.append(tweet)
    return updated_tweets


@click.group()
def cli():
    pass


@cli.command()
@click.option("--config-file", "-c", type=click.Path(exists=True), default="config.json", help="configuration file")
@click.option("--debug", "-d", is_flag=True, help="debug output mode")
@click.option("--destination", "-d", type=click.Path(exists=True), help="folder to download image(s)")
@click.option("--filename", "-f", type=click.STRING, help="filename or filename template")
@click.option('--write-changes', '-w', is_flag=True, help='write changes to JSON file with tweets')
@click.option('--update', '-u', is_flag=True, help='update tweet images, if they are already exist')
@click.argument('tweets-file', type=click.Path(exists=True))
def process(config_file: str, debug: bool, destination: str, filename: str, write_changes: bool, update: bool,
            tweets_file: str):
    """
    Processes JSON file with tweets.
    """
    app_config = prepare_config(config_file, destination, filename, update)

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug mode")

    logger.debug(f"Loading tweets from file {tweets_file}...")
    cli_tweets = models.TweetList()
    cli_tweets.load_from_file(tweets_file)

    logger.debug(f"Validating tweets from file {tweets_file}...")
    try:
        cli_tweets.validate()
    except DataError as e:
        logger.error(e)
        exit(1)

    logger.debug(f"Processing {len(cli_tweets.tweets)} tweets, loaded from file {tweets_file}...")
    updated_tweets = process_tweets(app_config, cli_tweets)

    if write_changes:
        logger.debug(f"Writing {len(updated_tweets.tweets)} tweets to file {tweets_file}...")
        updated_tweets.save_to_file(tweets_file)

    logger.debug(f"Processing {len(cli_tweets.tweets)} tweets finished.")


@cli.command()
@click.option("--config-file", "-c", type=click.Path(exists=True), default="config.json", help="configuration file")
@click.option("--debug", "-d", is_flag=True, help="debug output mode")
@click.option("--destination", "-d", type=click.Path(exists=True), help="folder to download image(s)")
@click.option("--filename", "-f", type=click.STRING, help="filename or filename template")
@click.argument('tweets', nargs=-1)
def shot(config_file: str, debug: bool, destination: str, filename: str, tweets: tuple):
    """
    Screenshots and saves tweet(s), that passed as parameter(s).
    """
    app_config = prepare_config(config_file, destination, filename)

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug mode")

    logger.debug(f"Loading tweets from CLI, {len(tweets)} URLs found.")
    cli_tweets = models.TweetList()
    cli_tweets.tweets = list()
    for tweet_url in tweets:
        clean_tweet_url = TwitterEmbedAPI.clean_tweet_url(tweet_url)
        tweet = models.Tweet({
            "url": clean_tweet_url
        })
        cli_tweets.tweets.append(tweet)

    logger.debug("Validating tweets from CLI...")
    try:
        cli_tweets.validate()
    except DataError as e:
        logger.error(e)
        exit(1)

    logger.debug(f"Processing {len(cli_tweets.tweets)} tweets, loaded from CLI...")
    process_tweets(app_config, cli_tweets)
    logger.debug(f"Processing {len(cli_tweets.tweets)} tweets finished.")


if __name__ == "__main__":
    cli()
