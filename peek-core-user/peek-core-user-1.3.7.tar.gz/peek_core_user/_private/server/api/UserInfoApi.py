import logging
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.storage.InternalUserGroupTuple import \
    InternalUserGroupTuple
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_core_user.server.UserInfoApiABC import UserInfoApiABC
from peek_core_user.tuples.GroupDetailTuple import GroupDetailTuple
from peek_core_user.tuples.UserDetailTuple import UserDetailTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class UserInfoApi(UserInfoApiABC):
    #: A reference to the core device plugins API
    _deviceApi: DeviceApiABC

    _userCopyFields = (
            set(UserDetailTuple.tupleFieldNames())
            & set(InternalUserTuple.tupleFieldNames())
    )

    _groupCopyFields = (
            set(GroupDetailTuple.tupleFieldNames())
            & set(InternalGroupTuple.tupleFieldNames())
    )

    def __init__(self, deviceApi: DeviceApiABC, dbSessionCreator):
        self._deviceApi = deviceApi
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def user(self, userName: str):
        """
        :returns a Deferred firing with Optional[UserDetailTuple]]
        """
        return self.userBlocking(userName)

    def userBlocking(self, userName, ormSession=None) -> Optional[UserDetailTuple]:

        if ormSession:
            close = False

        else:
            ormSession = self._dbSessionCreator()
            close = True

        try:
            user = (ormSession.query(InternalUserTuple)
                    .filter(InternalUserTuple.userName == userName)
                    .one())

            return self._makeUserDetails(user)

        except NoResultFound:
            return None

        finally:
            if close:
                ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def users(self, likeTitle: Optional[str] = None,
              groupNames: Optional[List[str]] = None):
        """
        Returns Deferred[List[UserDetailTuple]]
        """
        ormSession = self._dbSessionCreator()
        try:
            return self.usersBlocking(ormSession, likeTitle, groupNames)
        finally:
            ormSession.close()

    def usersBlocking(self, session, likeTitle: Optional[str] = None,
                      groupNames: Optional[List[str]] = None) -> List[
        UserDetailTuple]:
        qry = (
            session
                .query(InternalUserTuple)
                .options(subqueryload(InternalUserTuple.groups))
                .order_by(InternalUserTuple.userName)
        )

        if groupNames:
            qry = (
                qry.join(InternalUserGroupTuple)
                    .join(InternalGroupTuple)
                    .filter(InternalGroupTuple.groupName.in_(groupNames))
            )

        if likeTitle:
            qry = qry.filter(or_(
                InternalUserTuple.userTitle.ilike('%' + likeTitle + '%'),
                InternalUserTuple.userName.ilike('%' + likeTitle + '%')
            ))

        ormUsers = qry.all()

        return [self._makeUserDetails(u) for u in ormUsers]

    def _makeUserDetails(self, ormUser: InternalUserTuple) -> UserDetailTuple:
        userDetail = UserDetailTuple()
        for fieldName in self._userCopyFields:
            setattr(userDetail, fieldName, getattr(ormUser, fieldName))

        userDetail.groupNames = [g.groupName for g in ormUser.groups]
        return userDetail

    @deferToThreadWrapWithLogger(logger)
    def groups(self, likeTitle: Optional[str] = None):
        """
        Returns Deferred[List[UserDetailTuple]]
        """
        ormSession = self._dbSessionCreator()
        try:
            return self.groupsBlocking(ormSession, likeTitle)
        finally:
            ormSession.close()

    def groupsBlocking(self, session, likeTitle: Optional[str] = None) -> List[
        GroupDetailTuple]:
        qry = (
            session
                .query(InternalGroupTuple)
                .order_by(InternalGroupTuple.groupName)
        )

        if likeTitle:
            qry = qry.filter(InternalGroupTuple.userTitle.ilike('%' + likeTitle + '%'))

        return [self._makeGroupDetails(u) for u in qry.all()]

    def _makeGroupDetails(self, ormGroups: InternalGroupTuple) -> GroupDetailTuple:
        groupDetail = GroupDetailTuple()
        for fieldName in self._groupCopyFields:
            setattr(groupDetail, fieldName, getattr(ormGroups, fieldName))

        return groupDetail

    @deferToThreadWrapWithLogger(logger)
    def peekDeviceTokenForUser(self, userName: str) -> Optional[str]:
        session = self._dbSessionCreator()
        try:
            result = (session.query(UserLoggedIn)
                      .filter(UserLoggedIn.userName == userName)
                      .one())

            return result.deviceToken

        except NoResultFound:
            return None

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def peekUserForDeviceToken(self, deviceToken) -> Optional[UserDetailTuple]:
        session = self._dbSessionCreator()
        try:
            result = (
                session
                    .query(InternalUserTuple)
                    .join(UserLoggedIn,
                          UserLoggedIn.userName == InternalUserTuple.userName)
                    .filter(UserLoggedIn.deviceToken == deviceToken)
                    .one()
            )

            return self._makeUserDetails(result)

        except NoResultFound:
            return None

        finally:
            session.close()
