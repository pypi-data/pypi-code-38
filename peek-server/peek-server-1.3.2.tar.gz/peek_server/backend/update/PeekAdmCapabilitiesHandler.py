
# from peek_platform import PeekPlatformConfig
# from peek_server.backend.navbar.PeekAdmNavbarHandler import navbarDataHandler
# from vortex.DataWrapTuple import DataWrapTuple
# from vortex.Payload import Payload
# from vortex.PayloadEndpoint import PayloadEndpoint
# from vortex.VortexABC import SendVortexMsgResponseCallable
#
# capabilitiesDataFiltKey = {
#     "plugin": "peek_server",
#     "key": "admin.capabilities.data"
# }

#
# # HANDLER
# class __CrudHandler():
#     def __init__(self, payloadFilter):
#         self._payloadFilter = payloadFilter
#         self._ep = PayloadEndpoint(self._payloadFilter, self.process)
#
#     def process(self, payload,
#                 vortexUuid,
#                 httpSession,
#                 sendResponse: SendVortexMsgResponseCallable,
#                               **kwargs):
#         # from peek_server.server.auth import AuthValue
#         from peek_server.storage.Setting import internalSetting, CAPABILITIES_KEY
#
#         result = None
#         from peek_server.storage import dbConn
#         session = dbConn.ormSessionCreator
#
#         # Force capabilities reload on page load
#         PeekPlatformConfig.config._capabilities = None
#
#         # This is an update
#         if payload.tuples:
#             dataWrapTuple = payload.tuples[0]
#             self._capabilities = None
#
#             # try:
#             #     AuthValue.loadCapabilities(self, dataWrapTuple.data)
#             # except Exception as e:
#             #     pass
#             if self._capabilities is None:
#                 result = {"success": False,
#                           "message": "The license entered is not valid for this server"}
#                 sendResponse(Payload(filt=self._payloadFilter,
#                                           result=result).toVortexMsg())
#                 return
#
#             PeekPlatformConfig.config._capabilities = self._capabilities
#
#             internalSetting()[CAPABILITIES_KEY] = dataWrapTuple.data
#             session.commit()
#             result = {"success": True,
#                       "message": "The license was successfully loaded"}
#         dataWrapTuple = DataWrapTuple()
#         dataWrapTuple.data = PeekPlatformConfig.config.capabilities
#
#         sendResponse(Payload(filt=self._payloadFilter,
#                                   tuples=[dataWrapTuple],
#                                   result=result).toVortexMsg())
#
#         navbarDataHandler.sendModelUpdate(vortexUuid=vortexUuid)
#
#
# __ormCrudHandler = __CrudHandler(capabilitiesDataFiltKey)
