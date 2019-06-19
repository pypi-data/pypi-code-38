import logging

from sanic import Blueprint, Sanic
from sanic.request import Request
from sanic.exceptions import Forbidden

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)
token_configuration = Blueprint('Tokens Configuration')  # pylint: disable=invalid-name


class TokenConfigurationException(Exception):
    pass


def token_requred(async_handler):
    """
    token auth decorator
    call function(request, kwargs)
    """

    async def wrapped(request: Request, **kwargs):

        if request.args.get('token') not in request.app.config.TOKEN_LIST:
            raise Forbidden("Please, use right token in request")
        return await async_handler(request, **kwargs)

    return wrapped


@token_configuration.listener('before_server_start')
async def parse_token_list_logic(sanic_app: Sanic, _loop) -> None:
    env_token_list: str = sanic_app.config.pop('TOKEN_LIST', '')
    token_list = env_token_list.split(',')
    sanic_app.config.TOKEN_LIST = token_list
