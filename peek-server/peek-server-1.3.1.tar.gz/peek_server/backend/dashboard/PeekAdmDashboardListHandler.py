# '''
# Created on 09/07/2014
#
# @author: synerty
# '''
#
# # from peek_server.server.live_db.LiveDb import liveDb
# # from peek_server.server.orm.LiveDb import LiveDbKey
# # from peek_server.server.orm.AgentData import AgentImportDispGridInfo
# # from peek_server.server.orm.Display import DispBase
# # from peek_server.server.orm.GridKeyIndex import GridKeyCompilerQueue, DispIndexerQueue
# from txhttputil.util.DeferUtil import deferToThreadWrap
# from vortex.handler.ModelHandler import ModelHandler
#
# import logging
# from vortex.DeferUtil import deferToThreadWrapWithLogger
#
# logger = logging.getLogger(__name__)
#
# executeListDataKey = {'plugin': 'peek_server',
#                       'key': "peakadm.dashboard.list.data"}
#
#
# class DashboardListHandler(ModelHandler):
#
##   @deferToThreadWrapWithLogger(logger)
#     def buildModel(self, payloadFilt, **kwargs):
#         qryItems = []
#
#         from peek_server.storage import dbConn
#         session = dbConn.ormSessionCreator()
#
#         def rowsQuick(Declarative):
#             sql = '''
#                   SELECT 50 * count(*) AS estimate
#                   FROM "%s" TABLESAMPLE SYSTEM (2);
#                   '''
#             sql %= Declarative.__table__.name
#             return session.execute(sql).fetchone()[0]
#
#         def rows(Declarative, quick=False):
#             if quick:
#                 return rowsQuick(Declarative)
#
#             return session.query(Declarative).count()
#
#         # qryItems.append(("Grid Compiler Queue Size", GridKeyCompilerQueue, False))
#         # qryItems.append(("Display Compiler Queue Size", DispIndexerQueue, False))
#         # qryItems.append(("Display Agent Imported Grids", AgentImportDispGridInfo, False))
#         # qryItems.append(("Display Objects (Estimate)", DispBase, True))
#         # qryItems.append(("Live DB Values (Estimate)", LiveDbKey, True))
#
#         session.close()
#
#         data = [dict(desc=desc, value=rows(Declarative, quick))
#                 for desc, Declarative, quick in qryItems]
#
#         # from peek_server.server.queue_processesors.GridKeyQueueCompiler import gridKeyQueueCompiler
#         # data.append(dict(desc="Grid Compiler Status",
#         #                  value=gridKeyQueueCompiler.statusText()))
#         #
#         # from peek_server.server.queue_processesors.DispQueueIndexer import dispQueueCompiler
#         # data.append(dict(desc="Display Compiler Status",
#         #                  value=dispQueueCompiler.statusText()))
#
#         # data.extend([dict(desc=i[0], value=i[1]) for i in liveDb.statusNameValues])
#
#         return data
#
#
# dashboardListHandler = DashboardListHandler(executeListDataKey)
