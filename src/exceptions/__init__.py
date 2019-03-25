class AppConfigValidationError(Exception):
    pass


class TwitterAPIRequestError(Exception):
    def __init__(self, url, method, status_code, body):
        message = f"{method} {url}: Response {status_code} ({body})"
        super().__init__(message)


class ImageProcessorException(Exception):
    pass


class HeadlessBrowserException(Exception):
    pass


class TwitsConfigValidationError(Exception):
    pass
