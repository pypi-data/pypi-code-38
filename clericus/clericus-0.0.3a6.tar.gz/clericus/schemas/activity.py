import motor
import asyncio
import bson
import datetime

from pymongo.errors import DuplicateKeyError
from ..errors import ClientError
from ..errors.mongo import parseDuplicateKeyError

from ..db.transactions import withSession
from ..parsing.fields import (
    ObjectIdField,
    StringField,
    DictField,
    DatetimeField,
)


async def createActivityCollection(db):
    try:
        await db.create_collection("activity")
    except:
        pass
    await db.command(
        "collMod",
        "activity",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "action", "actorID", "targetIDs", "targetType", "payload"
                ],
                "properties": {
                    "action": {
                        "bsonType": "string",
                    },
                    "actorID": {
                        "bsonType": "objectId",
                    },
                    "targetIDs": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "objectId",
                        },
                    },
                    "targetType": {
                        "bsonType": "string",
                    },
                    "payload": {
                        "bsonType": "object",
                    },
                }
            }
        }
    )

    await asyncio.wait([
        db.activity.create_index([("actorID", 1)], ),
        db.activity.create_index([("targetIDs", 1)], ),
    ])


@withSession
async def createActivity(
    db,
    action: str,
    actorID: bson.ObjectId,
    targetIDs,
    targetType: str,
    payload: dict,
    session=None,
):
    activity = {
        "action": action,
        "actorID": actorID,
        "targetIDs": targetIDs,
        "targetType": targetType,
        "payload": payload,
    }
    try:
        result = await db.activity.insert_one(
            activity,
            session=session,
        )
        activity["_id"] = result.inserted_id

        return activity

    except Exception as err:
        raise err
