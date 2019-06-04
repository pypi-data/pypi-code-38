import logging
from typing import Optional, List

from rx import Observable
from rx.subjects import Subject
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger, noMainThread

from peek_core_device._private.server.controller.MainController import MainController
from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_device.tuples.DeviceDetailTuple import DeviceDetailTuple
from peek_core_device.tuples.DeviceOnlineDetailTuple import DeviceOnlineDetailTuple

logger = logging.getLogger(__name__)


class DeviceApi(DeviceApiABC):
    def __init__(self, mainController: MainController,
                 ormSessionCreator):
        self._mainController = mainController
        self._ormSessionCreator = ormSessionCreator

        self._deviceOnlineSubject = Subject()

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def deviceDetails(self, deviceTokens: List[str]) -> Deferred:
        ormSession = self._ormSessionCreator()
        try:
            all = ormSession.query(DeviceInfoTuple) \
                .filter(DeviceInfoTuple.deviceToken.in_(deviceTokens)) \
                .all()

            tuples = [
                DeviceDetailTuple(
                    deviceToken=d.deviceToken,
                    deviceType=d.deviceType,
                    description=d.description,
                    lastOnline=d.lastOnline,
                    isOnline=d.isOnline,
                )
                for d in all
            ]

            return tuples

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def deviceDescription(self, deviceToken: str) -> Deferred:
        return self.deviceDescriptionBlocking(deviceToken)

    def deviceDescriptionBlocking(self, deviceToken: str) -> Optional[str]:
        noMainThread()

        ormSession = self._ormSessionCreator()
        try:
            all = ormSession.query(DeviceInfoTuple) \
                .filter(DeviceInfoTuple.deviceToken == deviceToken) \
                .all()

            if not all:
                return None

            return all[0].description

        finally:
            ormSession.close()

    def deviceOnlineStatus(self) -> Observable:
        return self._deviceOnlineSubject

    def notifyOfOnlineStatus(self, deviceId: str, deviceToken: str, status: bool):
        self._deviceOnlineSubject.on_next(
            DeviceOnlineDetailTuple(
                deviceToken=deviceToken,
                deviceId=deviceId,
                onlineStatus=status
            )
        )
