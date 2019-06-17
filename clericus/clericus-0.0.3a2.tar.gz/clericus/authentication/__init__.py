from aiohttp import web
from typing import Dict
from ..parsing import RequestParser


def setCurrentUser(response: web.Response, user: Dict) -> web.Response:
    return response


# class CurrentUserField():


class AuthenticatedRequestParser(RequestParser):
    currentUser = None
