import logging
import uuid
from datetime import datetime
from typing import List

import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import subqueryload
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_core_user._private.server.controller.PasswordUpdateController import \
    PasswordUpdateController
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.tuples.InternalUserImportResultTuple import \
    InternalUserImportResultTuple
from peek_core_user._private.worker.CeleryApp import celeryApp
from peek_core_user.tuples.import_.ImportInternalUserTuple import \
    ImportInternalUserTuple
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def importInternalUsers(self, importHash: str,
                        usersVortexMsg: bytes) -> InternalUserImportResultTuple:
    """ Import Internal Users

    :param self: A celery reference to this task
    :param importHash: An unique string of this group of items being imported.
    :param usersVortexMsg: A vortexMsg containing the user tuples
    :returns: A list of grid keys that have been updated.
    """

    importUsers: List[ImportInternalUserTuple] = (
        Payload()
            .fromEncodedPayload(usersVortexMsg)
            .tuples
    )

    startTime = datetime.now(pytz.utc)

    session = CeleryDbConn.getDbSession()
    try:
        same = []
        updates = []
        deleteIds = []
        inserts = []
        errors = []

        # This will remove duplicates
        allNames = [i.userName for i in importUsers]

        if not allNames:
            existingUsersByName = {}

        else:
            existingUsersByName = {
                g.userName: g for g in
                session
                    .query(InternalUserTuple)
                    .filter(InternalUserTuple.userName.in_(allNames))
                    .filter(InternalUserTuple.importHash == importHash)
                    .options(subqueryload(InternalUserTuple.groups))
                    .all()
            }

        groupsByName = {
            g.groupName: g for g in
            session.query(InternalGroupTuple).all()
        }

        for importUser in importUsers:
            try:
                existingUser = existingUsersByName.pop(importUser.userName, None)
                if existingUser:
                    _updateUser(existingUser, groupsByName, importUser, same, updates)

                else:
                    _insertUser(session, groupsByName, importUser, importHash, inserts)

                session.commit()

            except IntegrityError as e:
                errors.append(str(e))
                session.rollback()

        for oldUser in existingUsersByName.values():
            deleteIds.append(oldUser.id)
            session.delete(oldUser)

        session.commit()

        logger.debug("Inserted %s, Updated %s, Deleted %s, Same %s, in %s",
                    len(inserts), len(updates), len(deleteIds), len(same),
                    (datetime.now(pytz.utc) - startTime))

        return InternalUserImportResultTuple(
            addedIds=[o.id for o in inserts],
            updatedIds=[o.id for o in updates],
            deletedIds=deleteIds,
            sameCount=len(same),
            errors=errors
        )

    except Exception as e:
        session.rollback()
        logger.warning("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=2)

    finally:
        session.close()


def _insertUser(session, groupsByName, importUser, importHash, inserts):

    newUser = InternalUserTuple()
    newUser.importHash = importHash

    for fieldName in ImportInternalUserTuple.tupleFieldNames():
        setattr(newUser, fieldName, getattr(importUser, fieldName))

    if importUser.groupKeys is not None:
        for groupKey in importUser.groupKeys:
            newUser.groups.append(groupsByName[groupKey])

    newUser.password = PasswordUpdateController.hashPass(str(uuid.uuid4()))

    session.add(newUser)
    inserts.append(newUser)


def _updateUser(existingUser, groupsByName, importUser, same, updates):

    excludeFieldNames = ("groupKeys", "password")

    copyFields = filter(lambda f: f not in excludeFieldNames,
                        ImportInternalUserTuple.tupleFieldNames())

    updated = False
    for fieldName in copyFields:
        newVal = getattr(importUser, fieldName)
        if getattr(existingUser, fieldName) != newVal:
            setattr(existingUser, fieldName, newVal)
            updated = True

    # The password is an optional field
    if importUser.password is not None:
        existingUser.password = PasswordUpdateController.hashPass(importUser.password)
        updated = True

    # If there are NONE groups, then don't make any changes
    if importUser.groupKeys is not None:
        linkedGroupNames = set([g.groupName for g in existingUser.groups])
        addGroups = set(importUser.groupKeys) - linkedGroupNames
        removeGroups = linkedGroupNames - set(importUser.groupKeys)

        for addGroup in addGroups:
            existingUser.groups.append(groupsByName[addGroup])

        for removeGroup in removeGroups:
            existingUser.groups.remove(groupsByName[removeGroup])

        updated = updated or bool(addGroups) or bool(removeGroups)


    if updated:
        updates.append(existingUser)
    else:
        same.append(existingUser)
