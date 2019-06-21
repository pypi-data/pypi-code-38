import enum

from ..parsing.fields import ListField, ObjectIdField, DictField
from ..schemas.user import EmbeddedUserField


class Permissions(enum.Enum):
    NULL = None
    OWNER = "ownerIDs"
    VIEW = "viewerIDs"


def _toLookupKey(permission):
    if not permission.value.endswith("IDs"):
        raise Exception("Invalid permission type")
    return f"{permission.value[:-3]}s"


def permissionSelector(currentUser, permission):
    currentUserID = currentUser["_id"] if currentUser else None

    if permission == Permissions.VIEW:
        ors = [
            {
                "permissions.public": True
            },
        ]
        if currentUserID:
            ors += [
                {
                    f"permissions.{Permissions.OWNER.value}": currentUserID
                },
                {
                    f"permissions.{Permissions.VIEW.value}": currentUserID
                },
            ]
        return {"$or": ors}
    return {f"permissions.{permission.value}": currentUserID}


def lookupPermissionsStage(permissions: list):
    """
        Return a list of mongodb pipeline stages to lookup
        the given permission list on objects in the pipeline
    """
    pipeline = []
    for permission in permissions:
        pipeline += [
            {
                "$lookup": {
                    "from": "user",
                    "as": f"permissionUsers.{_toLookupKey(permission)}",
                    "localField": f"permissions.{permission.value}",
                    "foreignField": "_id",
                },
            },
        ]

    return pipeline


class PermissionField(DictField):
    def __init__(self, permissions, *args, **kwargs):
        super().__init__(
            fields={
                _toLookupKey(permission): ListField(EmbeddedUserField())
                for permission in permissions
            },
            *args,
            **kwargs,
        )


class Actions():
    def __init__(self, actions):
        self._actions = actions or {}

    def actions(self):
        return self._actions.keys()

    def canDoAction(
        self,
        action="",
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        try:
            return self._actions[action](
                currentUser=currentUser,
                targetObject=targetObject,
                **kwargs,
            )
        except KeyError:
            raise Exception(f"Unknown Action: {action}")

    def checkActions(
        self,
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        return {
            a: self.canDoAction(
                a,
                currentUser=currentUser,
                targetObject=targetObject,
                **kwargs,
            )
            for a in self.actions()
        }


def hasPermission(permission=Permissions.NULL, ):
    def check(
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        try:
            return currentUser["_id"] in targetObject["permissions"][
                permission.value]
        except:
            return False

    return check


def hasAllPermissions(*permissions):
    def check(
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        return all([
            hasPermission(p)(
                currentUser=currentUser,
                targetObject=targetObject,
                **kwargs,
            ) for p in permissions
        ])

    return check


def hasAnyPermissions(*permissions):
    def check(
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        return any([
            hasPermission(p)(
                currentUser=currentUser,
                targetObject=targetObject,
                **kwargs,
            ) for p in permissions
        ])

    return check


def orClause(*clauses):
    def check(
        currentUser=None,
        targetObject=None,
        **kwargs,
    ):
        return any([
            clause(
                currentUser=currentUser,
                targetObject=targetObject,
                **kwargs,
            ) for clause in clauses
        ])

    return check


def isPublic(
    currentUser=None,
    targetObject=None,
    **kwargs,
):
    try:
        return targetObject["permissions"]["public"] == True
    except:
        return False