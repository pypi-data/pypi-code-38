import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

import pytz
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTuple import \
    BranchLiveEditTuple
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTupleAction import \
    BranchLiveEditTupleAction
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from twisted.internet import task
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import vortexLogFailure
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class BranchLiveEditController(TupleActionProcessorDelegateABC):
    """ Branch Live Edit

    This controller just stores activly edited branches, and relays them between
    each other.

    """
    PERIOD = 30.000

    def __init__(self):
        self._tupleObservable = None

        #: This stores the cache of grid data for the clients
        self._cache: Dict[Tuple[str, int], BranchLiveEditTuple] = {}

        self._pollLoopingCall = task.LoopingCall(self._expireCheck)

    def start(self):
        d = self._pollLoopingCall.start(self.PERIOD, now=False)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def _timerErrback(self, failure):
        vortexLogFailure(failure, logger)

    def _expireCheck(self, _):
        # Clean out the old branch updates
        for key, item in list(self._cache.items()):
            if (datetime.now(pytz.utc) - item.serverUpdateDate).days:
                self._cache.pop(key)

    def shutdown(self):
        if not self._pollLoopingCall:
            self._pollLoopingCall.stop()

        self._pollLoopingCall = None

        self._tupleObservable = None
        self._cache = {}

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def updateBranch(self, branchTuple: BranchTuple):
        ts = TupleSelector(
            BranchLiveEditTuple.tupleType(), dict(
                coordSetId=branchTuple.coordSetId,
                key=branchTuple.key
            )
        )

        if not self._tupleObservable.hasTupleSubscribers(ts):
            return

        cacheKey = (branchTuple.coordSetId, branchTuple.key)

        liveEditTuple = BranchLiveEditTuple()
        liveEditTuple.branchTuple = branchTuple
        liveEditTuple.uiUpdateDate = branchTuple.updatedDate
        liveEditTuple.serverUpdateDate = datetime.now(pytz.utc)
        liveEditTuple.updateFromSave = True
        self._cache[cacheKey] = liveEditTuple

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        yield None

        assert isinstance(tupleAction, BranchLiveEditTupleAction), \
            "tupleAction is not BranchLiveEditTupleAction"

        # Ignore the updates
        if tupleAction.actionType == BranchLiveEditTupleAction.EDITING_STARTED:
            return

        coordSetId = tupleAction.branchTuple.coordSetId
        key = tupleAction.branchTuple.key

        tuple_ = BranchLiveEditTuple()
        tuple_.branchTuple = tupleAction.branchTuple
        tuple_.updatedByUser = tupleAction.updatedByUser
        tuple_.uiUpdateDate = tupleAction.dateTime
        tuple_.serverUpdateDate = datetime.now(pytz.utc)
        tuple_.updateFromSave = False

        self._cache[(coordSetId, key)] = tuple_

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(BranchLiveEditTuple.tupleName(), {
                "coordSetId": coordSetId,
                "key": key
            })
        )

    def getLiveEditTuple(self, coordSetId, key) -> Optional[BranchLiveEditTuple]:
        return self._cache.get((coordSetId, key))
