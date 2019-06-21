from ..handler import Method, Endpoint
from ..parsing import (
    RequestParser,
    DictParser,
    ResponseSerializerWithErrors,
)
from ..parsing.fields import (
    StringField,
    Field,
    ListField,
    DictField,
    BoolField,
    ObjectIdField,
)


from ..schemas.permissions import (permissionSelector, lookupPermissionsStage, Permissions, PermissionField,)

from ..errors import ServerError, ClientError
import datetime
import bson


def generatePublishEndpoint(
    collectionName,
    permissionsList,
):
    class PublishEndpoint(Endpoint):
        class Post(Method):
            # class Parser(RequestParser):
            # class BodyParser(DictParser):
            #     objectID = ObjectIdField()

            class Serializer(ResponseSerializerWithErrors):
                permissions = DictField(
                    fields={
                        "_id": ObjectIdField(serializeTo="id"),
                        "permissionUsers": PermissionField(permissionsList),
                        "isPublic": BoolField(),
                    }
                )

            async def process(
                self,
                objectID: bson.ObjectId,
                currentUser,
            ):

                objectID = bson.ObjectId(objectID)

                selector = {
                    "$and": [
                        {
                            "_id": objectID
                        },
                        permissionSelector(
                            currentUser=currentUser,
                            permission=Permissions.OWNER,
                        ),
                    ]
                }

                pipeline = [
                    {
                        "$match": selector
                    },
                    {
                        "$addFields": {
                            "isPublic": {
                                "$eq": ["$permissions.public", True]
                            },
                        }
                    },
                ]
                pipeline += lookupPermissionsStage(permissionsList)

                items = await self.settings.db.get_collection(
                    collectionName
                ).aggregate(pipeline).to_list(1)

                if len(items) == 0:
                    raise ClientError(statusCode=404)

                result = await self.settings.db.get_collection(
                    collectionName
                ).update_one(
                    {"_id": objectID},
                    {"$set": {
                        "permissions.public": True
                    }},
                )

                items = await self.settings.db.get_collection(
                    collectionName
                ).aggregate(pipeline).to_list(1)

                return {"permissions": items[0]}

    return PublishEndpoint


def generateUnpublishEndpoint(
    collectionName,
    permissionsList,
):
    class UnpublishEndpoint(Endpoint):
        class Post(Method):
            # class Parser(RequestParser):
            # class BodyParser(DictParser):
            #     objectID = ObjectIdField()

            class Serializer(ResponseSerializerWithErrors):
                permissions = DictField(
                    fields={
                        "_id": ObjectIdField(serializeTo="id"),
                        "permissionUsers": PermissionField(permissionsList),
                        "isPublic": BoolField(),
                    }
                )

            async def process(
                self,
                objectID: bson.ObjectId,
                currentUser,
            ):

                objectID = bson.ObjectId(objectID)

                selector = {
                    "$and": [
                        {
                            "_id": objectID
                        },
                        permissionSelector(
                            currentUser=currentUser,
                            permission=Permissions.OWNER,
                        ),
                    ]
                }

                pipeline = [
                    {
                        "$match": selector
                    },
                    {
                        "$addFields": {
                            "isPublic": {
                                "$eq": ["$permissions.public", True]
                            },
                        }
                    },
                ]
                pipeline += lookupPermissionsStage(permissionsList)

                items = await self.settings.db.get_collection(
                    collectionName
                ).aggregate(pipeline).to_list(1)

                if len(items) == 0:
                    raise ClientError(statusCode=404)

                result = await self.settings.db.get_collection(
                    collectionName
                ).update_one(
                    {"_id": objectID},
                    {"$set": {
                        "permissions.public": False
                    }},
                )

                items = await self.settings.db.get_collection(
                    collectionName
                ).aggregate(pipeline).to_list(1)

                return {"permissions": items[0]}

    return UnpublishEndpoint


def generateActionsEndpoint(
    collectionName,
    actions,
):
    class CheckPermissionsEndpoint(Endpoint):
        class Get(Method):
            class Parser(RequestParser):
                class UrlParser(DictParser):
                    objectID = ObjectIdField()

            class Serializer(ResponseSerializerWithErrors):
                actions = DictField(fields={})

            async def process(
                self,
                objectID: bson.ObjectId,
                currentUser=None,
            ):

                targetObject = await self.settings.db.get_collection(
                    collectionName
                ).find_one(objectID)

                response = actions.checkActions(
                    currentUser=currentUser,
                    targetObject=targetObject,
                )

                return {"actions": response}

    return CheckPermissionsEndpoint