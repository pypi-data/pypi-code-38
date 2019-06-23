import logging

import ujson
from peek_plugin_diagram._private.server.controller.BranchLiveEditController import \
    BranchLiveEditController
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.tuples.branch.BranchKeyToIdMapTuple import \
    BranchKeyToIdMapTuple
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTuple import \
    BranchLiveEditTuple
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from peek_plugin_diagram._private.tuples.branch.BranchUpdateTupleAction import \
    BranchUpdateTupleAction
from peek_plugin_diagram._private.worker.tasks.branch.BranchIndexImporter import \
    createOrUpdateBranches
from peek_plugin_diagram._private.worker.tasks.branch.BranchIndexUpdater import \
    updateBranches
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, Deferred
from vortex.DeferUtil import vortexLogAndConsumeFailure
from vortex.Payload import Payload
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class BranchUpdateController(TupleActionProcessorDelegateABC):
    """ Branch Update Controller

    This controller handles the branch updates from the UI

    """

    def __init__(self, liveDbWriteApi: LiveDBWriteApiABC,
                 tupleObservable: TupleDataObservableHandler,
                 liveEditController: BranchLiveEditController,
                 dbSessionCreator):
        self._liveDbWriteApi = liveDbWriteApi
        self._tupleObservable = tupleObservable
        self._liveEditController = liveEditController
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        self._liveDbWriteApi = None
        self._tupleObservable = None
        self._liveEditController = None
        self._dbSessionCreator = None

    @inlineCallbacks
    def updateBranch(self, branchEncodedPayload: bytes):
        yield None
        raise NotImplemented("BranchUpdateController.updateBranch")

    @inlineCallbacks
    def importBranches(self, branchesEncodedPayload: bytes):
        yield createOrUpdateBranches.delay(branchesEncodedPayload)

        self._updateBranchKeyToIdMap()

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        if not isinstance(tupleAction, BranchUpdateTupleAction):
            raise Exception("Unhandled tuple action %s" % tupleAction)

        logger.debug("Received branch save for branch %s by %s",
                     tupleAction.branchTuple.key,
                     tupleAction.branchTuple.updatedByUser)

        d = self.__processUpdateFromClient(tupleAction)
        d.addErrback(vortexLogAndConsumeFailure, logger)
        return defer.succeed([])

    @inlineCallbacks
    def __processUpdateFromClient(self, tupleAction: TupleActionABC) -> Deferred:

        dbSession = self._dbSessionCreator()
        try:
            encodedPayload = yield Payload(tuples=[tupleAction.branchTuple]) \
                .toEncodedPayloadDefer()

            yield updateBranches.delay(tupleAction.modelSetId, encodedPayload)

            # Load the branch from the DB and tell the LiveDb update
            # that there is an update.
            branchIndex = dbSession.query(BranchIndex) \
                .filter(BranchIndex.coordSetId == tupleAction.branchTuple.coordSetId) \
                .filter(BranchIndex.key == tupleAction.branchTuple.key) \
                .one()

            branchTuple = BranchTuple.loadFromJson(branchIndex.packedJson,
                                                   branchIndex.importHash,
                                                   branchIndex.importGroupHash)

            self._liveEditController.updateBranch(branchTuple)

            self._updateBranchKeyToIdMap()

            self._tupleObservable.notifyOfTupleUpdate(
                TupleSelector(
                    BranchLiveEditTuple.tupleType(), dict(
                        coordSetId=tupleAction.branchTuple.coordSetId,
                        key=tupleAction.branchTuple.key
                    )
                )
            )

        except Exception as e:
            logger.exception(e)

        finally:
            dbSession.close()

    def _updateBranchKeyToIdMap(self):
        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(BranchKeyToIdMapTuple.tupleType(), {})
        )
