import logging
import time
from abc import abstractmethod, ABC
from functools import partial

import jwt
from botocore.exceptions import ClientError, EndpointConnectionError
from flask import request, session, current_app
from munch import munchify
from probator.constants import HTTP, ROLE_ADMIN
from probator.plugins.collectors.aws import AWSBaseRegionCollector, AWSBaseAccountCollector
from probator.plugins.views import BaseView
from probator.utils import has_access, get_jwt_key_data


class BaseWrapper(ABC):
    """Base wrapper class, setting up a logger, as well as default `__get__` method

    Attributes:
        log (logging.Logger): An instance of logging.Logger
        func (`function`): A reference to the wrapped function
    """

    def __init__(self, *args):
        self.log = logging.getLogger('.'.join((
            self.__class__.__module__,
            self.__class__.__name__
        )))

        if not args:
            self.func = None
        else:
            if callable(args[0]):
                self.func = args[0]

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class retry(BaseWrapper):
    """Decorator class to handle retrying calls if an exception occurs, with an exponential backoff. If the function
    fails to execute without raising an exception 3 times, the exception is re-raised
    """

    def __init__(self, *args):
        super().__init__(*args)
        self._tries = 2
        self._delay = 4
        self._backoff = 2

    def __backoff(self):
        self._tries -= 1

        if self._tries <= 0:
            return False

        time.sleep(self._delay)
        self._delay *= self._backoff

        return True

    def __call__(self, *args, **kwargs):
        self._tries = 2
        throttled = 0

        while self._tries > 0:
            try:
                return self.func(*args, **kwargs)
            except ClientError as ex:
                rex = str(ex.response['Error']['Code'])

                if 'OptInRequired' in rex:
                    worker = args[0]

                    if issubclass(worker.__class__, AWSBaseRegionCollector):
                        self.log.info(f'Opt-in required for {worker.account.account_name} / {worker.region} / {self.func.__name__}')

                    elif issubclass(worker.__class__, AWSBaseAccountCollector):
                        self.log.info(f'Opt-in required for {worker.account.account_name} / {self.func.__name__}')

                    else:
                        self.log.info(ex)

                    break

                elif 'AccessDenied' in rex or 'AuthFailure' in rex:
                    self.log.warning(f'Access denied. Ensure role trust and permissions are correct: {ex}')
                    break

                elif 'Throttling' in rex:
                    time.sleep(pow(2, throttled))
                    throttled += 1

                if not self.__backoff():
                    raise

            except OSError:
                self.log.exception('Retrying after OSError')
                if not self.__backoff():
                    raise

            except EndpointConnectionError as ex:
                self.log.error(ex)
                break


class rollback(BaseWrapper):
    """Decorator class to handle rolling back database transactions after a function is done running. If the wrapped
    function is a member of a BaseView class it will also return any exceptions as a proper API resopnse, else re-raise
    the exception thrown.

    Due to a caching mechanic within SQLAlchemy, we perform a rollback on every request regardless or we might end
    up getting stale data from a cached connection / existing transaction instead of live data.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.db = None

        if 'db' not in locals():
            from probator.database import db
            self.db = db

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)

        except Exception as ex:
            self.log.exception(ex)
            if issubclass(args[0].__class__, BaseView):
                return BaseView.make_response(str(ex), HTTP.BAD_REQUEST)
            else:
                raise

        finally:
            self.db.session.rollback()


class check_auth(BaseWrapper):
    """Decorator class to handle authentication checks for API endpoints. If the user is not authenticated it will
    return a 401 UNAUTHORIZED response to the user
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.role = ROLE_ADMIN

        if isinstance(args[0], str):
            self.role = args[0]

        elif len(args) > 1:
            self.role = args[1]

        else:
            raise ValueError(f'Invalid argument passed to check_auth: {args[0]} ({type(args[0])})')

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    def __check_auth(self, view):
        headers = {x[0]: x[1] for x in request.headers}
        if 'Authorization' in headers:
            try:
                if not session or 'user' not in session:
                    return view.make_unauth_response()

                token = munchify(jwt.decode(
                    headers['Authorization'],
                    get_jwt_key_data()
                ))

                if token.auth_system != current_app.active_auth_system.name:
                    self.log.error(f'Token is from {token.auth_system} but the active auth system is {current_app.active_auth_system.name}')

                    return view.make_unauth_response()

                if has_access(session['user'], self.role):
                    return

                self.log.error(f'User {session["user"].username} attempted to access page {request.path} without permissions')
                return view.make_unauth_response()

            except (jwt.DecodeError, jwt.ExpiredSignatureError) as ex:
                session.clear()
                view.log.info(f'Failed to decode signature or it had expired: {ex}')
                return view.make_unauth_response()

        session.clear()
        view.log.info('Failed to detect Authorization header')
        return view.make_unauth_response()

    def __call__(self, *args, **kwargs):
        # If called with without decorator arguments
        if args and isinstance(args[0], BaseView):
            auth = self.__check_auth(args[0])
            if auth:
                return auth

            return self.func(*args, **kwargs)

        # If called with decorator arguments
        else:
            def wrapped(*wargs, **wkwargs):
                func = args[0]
                wauth = self.__check_auth(wargs[0])
                if wauth:
                    return wauth

                return func(*wargs, **wkwargs)

            return wrapped
