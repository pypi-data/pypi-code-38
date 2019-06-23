import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List

import pytz
import shutil
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

from peek_core_device._private.server.controller.NotifierController import \
    NotifierController
from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device._private.storage.DeviceUpdateTuple import DeviceUpdateTuple
from peek_core_device._private.tuples.AlterDeviceUpdateAction import \
    AlterDeviceUpdateAction
from peek_core_device._private.tuples.CreateDeviceUpdateAction import \
    CreateDeviceUpdateAction
from peek_core_device._private.tuples.UpdateAppliedAction import UpdateAppliedAction
from txhttputil.site.SpooledNamedTemporaryFile import SpooledNamedTemporaryFile
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Tuple import Tuple
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class UpdateController:
    def __init__(self, dbSessionCreator,
                 notifierController: NotifierController,
                 deviceUpdateFilePath: Path):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = notifierController
        self._deviceUpdateFilePath = deviceUpdateFilePath

    def shutdown(self):
        pass

    def processTupleAction(self, tupleAction: TupleActionABC) -> List[Tuple]:

        if isinstance(tupleAction, AlterDeviceUpdateAction):
            return self._processAdminAlter(tupleAction)

        if isinstance(tupleAction, UpdateAppliedAction):
            return self._processDeviceUpdated(tupleAction)

    @deferToThreadWrapWithLogger(logger)
    def _processAdminAlter(self, action: AlterDeviceUpdateAction) -> List[Tuple]:
        """ Process Admin Update

        :rtype: Deferred
        """
        session = self._dbSessionCreator()
        try:
            deviceUpdate = (
                session.query(DeviceUpdateTuple)
                    .filter(DeviceUpdateTuple.id == action.updateId)
                    .one()
            )

            deviceType = deviceUpdate.deviceType

            if action.remove:
                session.delete(deviceUpdate)
            else:
                deviceUpdate.isEnabled = action.isEnabled

            session.commit()

            self._notifierController.notifyDeviceUpdate(deviceType=deviceType)

            return []

        finally:
            # Always close the session after we create it
            session.close()

    @inlineCallbacks
    def processCreateUpdateUpload(self, namedTempFile: SpooledNamedTemporaryFile,
                                  action: CreateDeviceUpdateAction):
        """ Process Create Update Upload

        Unlike the other action processes in the controllers, this method is called by
        a http resource upload.
        """

        if not zipfile.is_zipfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a zip file")

        # Create the file name
        filePath = '%s/%s.zip' % (
            action.newUpdate.deviceType, action.newUpdate.updateVersion)
        action.newUpdate.filePath = filePath
        action.newUpdate.urlPath = filePath.replace(r'\\', r'/')
        action.newUpdate.fileSize = Path(namedTempFile.name).stat().st_size

        # Create the database object, If that fails from some integrity problem
        # Then the file will delete it's self still
        deviceUpdateTuple = yield self._createUpdateOrmObj(action.newUpdate)

        absFilePath = self._deviceUpdateFilePath / filePath
        absFilePath.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(namedTempFile.name, str(absFilePath))
        namedTempFile.delete = False

        self._notifierController.notifyDeviceUpdate(
            deviceType=deviceUpdateTuple.deviceType
        )

        returnValue("%s:%s Created Successfully"
                    % (deviceUpdateTuple.deviceType, deviceUpdateTuple.updateVersion))

    @deferToThreadWrapWithLogger(logger)
    def _createUpdateOrmObj(self, newUpdate: DeviceUpdateTuple) -> DeviceUpdateTuple:
        """ Process Device Enrolment

        :rtype: Deferred
        """
        ormSession = self._dbSessionCreator()
        try:
            newUpdate.buildDate = datetime.now(pytz.utc)
            newUpdate.isEnabled = False
            ormSession.add(newUpdate)
            ormSession.commit()

            ormSession.refresh(newUpdate)
            ormSession.expunge_all()
            return newUpdate

        finally:
            ormSession.close()



    @deferToThreadWrapWithLogger(logger)
    def _processDeviceUpdated(self, action: UpdateAppliedAction) -> List[Tuple]:
        """ Process Device Updated

        This action is sent when the device has applied an update, or attempted to.

        :rtype: Deferred
        """
        session = self._dbSessionCreator()
        try:
            deviceInfo = (
                session.query(DeviceInfoTuple)
                    .filter(DeviceInfoTuple.deviceId == action.deviceId)
                    .one()
            )

            deviceId = deviceInfo.deviceId

            if action.appVersion is not None:
                deviceInfo.appVersion = action.appVersion

            if action.updateVersion is not None:
                deviceInfo.updateVersion = action.updateVersion

            session.commit()

            self._notifierController.notifyDeviceInfo(deviceId=deviceId)

            return []

        finally:
            session.close()