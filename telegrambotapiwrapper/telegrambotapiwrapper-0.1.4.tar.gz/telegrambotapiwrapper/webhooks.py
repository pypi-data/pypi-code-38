from telegrambotapiwrapper.typelib import Update
from telegrambotapiwrapper.response import handle_response
from telegrambotapiwrapper.annotation import AnnotationWrapper


def webhook_handler(request: str) -> Update:
    """Process a request from Telegram Bot Api containing Update.

    Args:
        request (str): string representing a request from Telegra Bot Api
    Return:
        (Update): update object
    Raises:
        RequestResultIsNotOk: if the answer contains no result
    """
    return handle_response(request, AnnotationWrapper("Update"))








