"""
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
import logging
import os

from twisted.web.server import NOT_DONE_YET
from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.StaticFileResource import StaticFileResource

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PeekSwInstallManagerABC import PeekSwInstallManagerABC

logger = logging.getLogger(__name__)


class PeekSwUpdateDownloadResource(BasicResource):
    isLeaf = True
    isGzipped = True

    def render_GET(self, request):
        componentName = request.args.get(b'name', [None])[0]
        version = request.args.get(b'version', [None])[0]

        if not componentName and not version:
            msg = "Download requires name and version, Name=%s, Version=%s"
            msg %= (componentName, version)
            logger.error(msg)
            request.write(msg.encode())
            request.finish()
            return NOT_DONE_YET

        componentName = componentName.decode()
        version = version.decode()

        logger.debug("Peek Platform Download Resource GET, name=%s, version=%s",
                     componentName, version)

        newSoftwareTar = PeekSwInstallManagerABC.makeReleaseFileName(version)

        request.responseHeaders.setRawHeaders(b'content-type',
                                              [b'application/octet-stream'])

        resource = StaticFileResource(newSoftwareTar)
        return resource.render_GET(request)


