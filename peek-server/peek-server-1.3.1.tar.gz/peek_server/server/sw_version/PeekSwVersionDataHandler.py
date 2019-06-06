import logging

from peek_platform import PeekPlatformConfig
from peek_platform.sw_version.PeekSwVersionPollHandler import peekPlatformVersionFilt
from peek_platform.sw_version.PeekSwVersionTuple import PeekSwVersionTuple
from peek_server.server.sw_version.PluginSwVersionInfoUtil import \
    getLatestPluginVersionInfos
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)


# -------------------------------------
# Software Update Handler for data from agents

# The filter we listen on

class PeekSwVersionDataHandler(object):
    def __init__(self, payloadFilter):
        self._ep = PayloadEndpoint(payloadFilter, self._process)

    def _process(self, sendResponse: SendVortexMsgResponseCallable, **kwargs):
        data = list()

        # First, name the platform version
        data.append(PeekSwVersionTuple(name="peek_platform",
                                       version=PeekPlatformConfig.config.platformVersion))

        for pluginVersionInfo in getLatestPluginVersionInfos():
            data.append(PeekSwVersionTuple(name=pluginVersionInfo.name,
                                           version=pluginVersionInfo.version))

        sendResponse(Payload(filt=peekPlatformVersionFilt, tuples=data).makePayloadEnvelope().toVortexMsg())

    def notifyOfVersion(self, name, version, vortexUuid=None):
        data = [PeekSwVersionTuple(name=name, version=version)]

        VortexFactory.sendVortexMsg(
            Payload(filt=peekPlatformVersionFilt, tuples=data).makePayloadEnvelope().toVortexMsg(),
            destVortexUuid=vortexUuid)


peekSwVersionDataHandler = PeekSwVersionDataHandler(peekPlatformVersionFilt)
