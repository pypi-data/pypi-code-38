""" 
 * view.common.uiobj.Style.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import json
import logging

from twisted.web.server import NOT_DONE_YET

from peek_core_device._private.server.controller.UpdateController import \
    UpdateController
from peek_core_device._private.tuples.CreateDeviceUpdateAction import \
    CreateDeviceUpdateAction
from txhttputil.site.BasicResource import BasicResource
from vortex.Payload import Payload

logger = logging.getLogger(name=__name__)


class DeviceUpdateUploadResource(BasicResource):
    isLeaf = True
    useLargeRequest = True

    UPDATE_TYPE_PLATFORM = 0
    UPDATE_TYPE_PLUGIN = 1

    def __init__(self, controller: UpdateController):
        BasicResource.__init__(self)
        self._controller = controller

    def render_GET(self, request):
        raise Exception("Updates must be done via the UI")

    def render_POST(self, request):
        request.responseHeaders.setRawHeaders('content-type', ['text/plain'])
        logger.info("Received device update upload request")

        action: CreateDeviceUpdateAction = Payload().fromVortexMsg(
            request.args[b'payload'][0]
        ).tuples[0]

        def good(data):
            request.write(json.dumps({'message': str(data)}).encode())
            request.finish()
            logger.info("Finished creating device update %s" % data)

        def bad(failure):
            e = failure.value
            logger.exception(e)

            request.write(json.dumps(
                {'error': str(failure.value),
                 'stdout': e.stdout if hasattr(e, 'stdout') else None,
                 'stderr': e.stderr if hasattr(e, 'stderr') else None}).encode())

            request.finish()

        d = self._controller.processCreateUpdateUpload(
            request.content.namedTemporaryFile,
            action
        )
        d.addCallbacks(good, bad)

        def closedError(failure):
            logger.error("Got closedError %s" % failure)

        request.notifyFinish().addErrback(closedError)

        return NOT_DONE_YET
