'''
Created on 09/07/2014

@author: synerty
'''

# import logging
# from vortex.DeferUtil import deferToThreadWrapWithLogger
#
# logger = logging.getLogger(__name__)

pluginVersionInfoHandlerKey = {
    'plugin': 'peek_server',
    'key': "peek_server.plugin.version.info"
}

#
# class __PluginVersionInfoHandler(ModelHandler):
#     @deferToThreadWrapWithLogger(logger)
#     def buildModel(self, payloadFilt, **kwargs):
#         return getLatestPluginVersionInfos()
#
#
# __pluginVersionInfoHandler = __PluginVersionInfoHandler(pluginVersionInfoHandlerKey)
