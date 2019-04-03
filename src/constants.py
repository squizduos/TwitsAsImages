# Got here: https://docs.python.org/3/library/logging.html
SUPPORTED_LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

SUPPORTED_HEADLESS_BROWSERS = ['phantomjs', 'chrome']
SUPPORTED_EMBED_TWEET_MAXSIZE = {"min_value": 220, "max_value": 550}
SUPPORTED_EMBED_TWEET_ALIGNS = ['left', 'right', 'center', 'none']
SUPPORTED_EMBED_TWEET_LANGUAGES = ["en", "ar", "bn", "cs", "da", "de", "el", "es", "fa", "fi", "fil", "fr", "he", "hi",
                                   "hu", "id", "it", "ja", "ko", "msa", "nl", "no", "pl", "pt", "ro", "ru", "sv", "th",
                                   "tr", "uk", "ur", "vi", "zh-cn", "zh-tw"]
SUPPORTED_EMBED_TWEET_THEMES = ['light', 'dark']
SUPPORTED_EMBED_TWEET_WIDGET_TYPES = ["video", ""]

TWEET_URL_REGEXP = r"(?P<protocol>http:\/\/|https:\/\/)?(?P<domain>twitter\.com)\/(?P<author>[A-Z,a-z,0-9,_]+)\/status\/(?P<id>[0-9]+)(?P<params>\/[\S]+|\?[\S]+)?"
