import logging
from datetime import datetime
from typing import List

import pytz
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.tuples.InternalGroupImportResultTuple import \
    InternalGroupImportResultTuple
from peek_core_user._private.worker.CeleryApp import celeryApp
from peek_core_user.tuples.import_.ImportInternalGroupTuple import \
    ImportInternalGroupTuple
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def importInternalGroups(self, importHash:str, groupsVortexMsg: bytes) -> InternalGroupImportResultTuple:
    """ Import Internal Groups

    :param self: A celery reference to this task
    :param importHash: An unique string of this group of items being imported.
    :param groupsVortexMsg: A vortexMsg containing the group tuples
    :returns: A list of grid keys that have been updated.
    """

    importGroups: List[ImportInternalGroupTuple] = (
        Payload()
            .fromEncodedPayload(groupsVortexMsg)
            .tuples
    )

    startTime = datetime.now(pytz.utc)

    session = CeleryDbConn.getDbSession()
    try:
        sameCount = 0
        updates = []
        deleteIds = []
        inserts = []
        errors = []

        # This will remove duplicates
        allNames = [i.groupName for i in importGroups]

        existingGroupsByName = {
            g.groupName: g for g in
            session
                .query(InternalGroupTuple)
                .filter(InternalGroupTuple.userName.in_(allNames))
                .filter(InternalGroupTuple.importHash == importHash)
                .all()
        }

        for importGroup in importGroups:
            existingGroup = existingGroupsByName.pop(importGroup.grouName, None)
            if existingGroup:
                updated = False
                for fieldName in ImportInternalGroupTuple.tupleFieldNames():
                    newVal = getattr(importGroup, fieldName)
                    if getattr(existingGroup, fieldName) != newVal:
                        setattr(existingGroup, fieldName, newVal)
                        updated = True

                if updated:
                    updates.append(existingGroup)
                else:
                    sameCount += 1

            else:
                newGroup = InternalGroupTuple()

                for fieldName in ImportInternalGroupTuple.tupleFieldNames():
                    setattr(newGroup, fieldName, getattr(importGroup, fieldName))

                session.add(newGroup)
                inserts.append(newGroup)

        for oldGroup in existingGroupsByName.values():
            deleteIds.append(oldGroup.id)
            session.delete(oldGroup)

        session.commit()
        logger.info("Inserted %s, Updated %s, Deleted %s, Same %s, in %s",
                    len(inserts), len(updates), len(deleteIds), sameCount,
                    (datetime.now(pytz.utc) - startTime))

        return InternalGroupImportResultTuple(
            addedIds=[o.id for o in inserts],
            updatedIds=[o.id for o in updates],
            deletedIds=deleteIds,
            sameCount=sameCount,
            errors=errors
        )

    except Exception as e:
        session.rollback()
        logger.warning("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=2)

    finally:
        session.close()
