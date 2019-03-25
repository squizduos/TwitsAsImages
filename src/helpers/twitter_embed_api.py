import re
import requests

import exceptions

TWITTER_URL_DATA_REGEXP = r"(http)?(s)?(:\/\/)?twitter\.com\/(?P<author>[A-Z,a-z,0-9,_]+)\/status\/(?P<id>[0-9]+)(\/)?"


class TwitterEmbedAPI:
    @staticmethod
    def get_twit_url_data(url: str) -> dict:
        found = re.search(TWITTER_URL_DATA_REGEXP, url)

        return found.groupdict()

    @staticmethod
    def get_twit_embed_html(url: str, embed_params: dict) -> str:
        embed_params['url'] = url
        r = requests.get('https://publish.twitter.com/oembed', params=embed_params)
        r.encoding = 'utf-8'
        if r.status_code != 200 or not r.json() or 'html' not in r.json():
            raise exceptions.TwitterAPIRequestError(r.url, "GET", r.status_code, r.text)
        return r.json().get('html')
