import os


class AppConfigValidationError(Exception):
    def __init__(self, json_file: str, error: Exception or None = None, custom_message: str = ""):
        base_message = f"Error while processing configuration file \"{os.path.abspath(json_file)}\""
        if custom_message:
            message = f"{base_message}: {custom_message}"
        elif error:
            message = f"{base_message}: original error message {str(error)}"
        else:
            message = f"{base_message}."
        super().__init__(message)


class TwitterAPIRequestError(Exception):
    def __init__(self, url, method, status_code, body):
        message = f"{method} {url}: Response {status_code} ({body})"
        super().__init__(message)


class ImageProcessorException(Exception):
    pass


class HeadlessBrowserException(Exception):
    pass


class TweetListValidationError(Exception):
    def __init__(self, json_file: str, error: Exception or None = None, custom_message: str = ""):
        base_message = f"Error while processing tweets file \"{os.path.abspath(json_file)}\""
        if custom_message:
            message = f"{base_message}: {custom_message}"
        elif error:
            message = f"{base_message}: original error message {str(error)}"
        else:
            message = f"{base_message}."
        super().__init__(message)
