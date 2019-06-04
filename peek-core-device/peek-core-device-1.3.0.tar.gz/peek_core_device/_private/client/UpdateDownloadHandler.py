# import shutil
# from pathlib import Path
#
# import logging
#
# from twisted.internet import defer
# from twisted.internet.defer import inlineCallbacks
#
# from peek_core_device._private.PluginNames import deviceFilt
# from txhttputil.downloader.HttpFileDownloader import HttpFileDownloader
# from vortex.DeferUtil import deferToThreadWrapWithLogger
#
# logger = logging.getLogger(__name__)
#
# _filt = dict(key="UpdateDownloadHandler")
# _filt.update(deviceFilt)
#
# class UpdateDownloadHandler(ModelHandler):
#     CHUNK_SIZE = 128000
#
#     def __init__(self, filtStoragePath:Path, serverHost:str, serverPort:int):
#         ModelHandler.__init__(self, payloadFilter=_filt)
#         self._filtStoragePath =  filtStoragePath
#         self._serverHost =  serverHost
#         self._serverPort =  serverPort
#
#     @inlineCallbacks
#     def buildModel(self, payloadFilt=None, vortexUuid=None, **kwargs):
#         chunk = payloadFilt["chunk"]
#         version = payloadFilt["version"]
#         deviceType = payloadFilt["deviceType"]
#         urlPath = payloadFilt["urlPath"]
#
#         localFile = self._filtStoragePath / deviceType / version
#
#         if localFile.is_file():
#             data = yield self._sendChunk(localFile, chunk)
#             defer.returnValue(data)
#
#         # If the file doesn't exist, download it from the server.
#         url = 'http://%(host)s:%(port)s/peek_core_device/device_update/%(urlPath)s'
#         url %= {'host':self._serverHost,
#                 'port':self._serverPort,
#                 'urlPath':urlPath}
#
#         logger.debug("Downloading file from %s" % url)
#         namedTempFile = yield HttpFileDownloader(url).run()
#         namedTempFile.delete = False
#         shutil.move(namedTempFile.name, str(localFile))
#
#         assert localFile.is_file(), "File download failed"
#
#         data = yield self._sendChunk(localFile, chunk)
#         defer.returnValue(data)
#
#     @deferToThreadWrapWithLogger(logger)
#     def _sendChunk(self, localFile:Path, chunk:int):
#         with localFile.open("rb") as f:
#             f.seek(chunk * self.CHUNK_SIZE)
#             return f.read(self.CHUNK_SIZE)