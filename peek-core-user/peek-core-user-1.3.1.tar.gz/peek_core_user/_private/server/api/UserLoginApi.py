import logging

from twisted.internet.defer import Deferred

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.server.controller.LoginLogoutController import \
    LoginLogoutController
from peek_core_user.server.UserLoginApiABC import UserLoginApiABC
from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction

logger = logging.getLogger(__name__)


class UserLoginApi(UserLoginApiABC):
    #: A reference to the core device plugins API
    _deviceApi: DeviceApiABC

    def __init__(self, loginLogoutController:LoginLogoutController):
        self._loginLogoutController = loginLogoutController

    def shutdown(self):
        pass

    def logout(self, logoutTuple: UserLogoutAction) -> Deferred:
        return self._loginLogoutController.logout(logoutTuple)


    def login(self, loginTuple: UserLoginAction) -> Deferred:
        return self._loginLogoutController.login(loginTuple)