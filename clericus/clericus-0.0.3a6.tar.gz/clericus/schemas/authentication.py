import motor
import bson
import asyncio
import bcrypt
import datetime

from pymongo.errors import DuplicateKeyError
from ..errors import ClientError
from ..errors.mongo import parseDuplicateKeyError
from ..db.transactions import withSession


async def createAuthenticationCollection(db):
    try:
        await db.create_collection("authentication")
    except:
        pass
    await db.command(
        "collMod",
        "authentication",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["userID", "passwordHash", "lastUpdated"],
                "properties": {
                    "userID": {
                        "bsonType": "objectId",
                    },
                    "passwordHash": {
                        "bsonType": "binData",
                    },
                    "lastUpdated": {
                        "bsonType": "date",
                    }
                }
            }
        }
    )

    await asyncio.wait([
        db.authentication.create_index(
            [("userID", 1)],
            unique=True,
            name="uniqueUserID",
        ),
    ])


@withSession
async def setPassword(
    db,
    session,
    userID: bson.ObjectId,
    password: str,
):
    try:
        #bcrypt wants bytes
        password = password.encode("utf-8")
    except:
        pass
    authentication = {
        "userID": userID,
        "passwordHash": bcrypt.hashpw(password, bcrypt.gensalt()),
        "lastUpdated": datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc
        )
    }
    result = await db.authentication.update_one(
        {"userID": userID},
        {
            "$set": authentication,
        },
        upsert=True,
        session=session,
    )
    # print(result.upserted_id)
    if result.upserted_id:
        authentication["_id"] = result.upserted_id
    elif result.matched_count == 1:
        authentication["_id"] = (
            await db.authentication.find_one({"userID": userID})
        )["_id"]
    else:
        raise Exception("Unable to set password")
    return authentication


@withSession
async def authenticateUser(
    db,
    session,
    email: str,
    password: str,
):
    try:
        #bcrypt wants bytes
        password = password.encode("utf-8")
    except:
        pass
    try:
        user = (
            await db.user.aggregate(
                pipeline=[
                    {
                        "$match": {
                            "email": email
                        }
                    },
                    # should be unnecessary
                    {
                        "$limit": 1
                    },
                    {
                        "$lookup": {
                            "localField": "_id",
                            "foreignField": "userID",
                            "from": "authentication",
                            "as": "authentication"
                        }
                    },
                    {
                        "$unwind": "$authentication"
                    },
                ],
                session=session,
            ).to_list(1)
        )[0]
    except:
        raise ClientError(
            message="Invalid Login",
            statusCode=401,
        )

    valid = bcrypt.checkpw(
        password,
        user["authentication"]["passwordHash"],
    )

    if not valid:
        raise ClientError(
            message="Invalid Login",
            statusCode=401,
        )

    # don't let the authentication info leave this function
    del user["authentication"]

    return user
