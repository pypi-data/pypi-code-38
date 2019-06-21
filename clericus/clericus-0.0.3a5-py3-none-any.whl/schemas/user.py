import motor
import asyncio

from pymongo.errors import DuplicateKeyError
from ..errors import ClientError
from ..errors.mongo import parseDuplicateKeyError

from ..db.transactions import withSession

from .authentication import setPassword

from ..parsing.fields import (
    ObjectIdField,
    StringField,
    DictField,
    DatetimeField,
)


async def createUserCollection(db):
    try:
        await db.create_collection("user")
    except:
        pass
    await db.command(
        "collMod",
        "user",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email"],
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "minLength": 1,
                        "description": "username cannot be blank"
                    },
                    "email": {
                        "bsonType": "string",
                        "minLength": 1,
                        "description": "username cannot be blank"
                    },
                }
            }
        }
    )

    await asyncio.wait([
        db.user.create_index(
            [("email", 1)],
            unique=True,
            name="uniqueEmail",
            collation={
                "locale": "en",
                "strength": 2
            },
        ),
        db.user.create_index(
            [("username", 1)],
            unique=True,
            name="uniqueUsername",
            collation={
                "locale": "en",
                "strength": 2
            },
        ),
    ])


@withSession
async def createUser(
    db,
    username: str,
    email: str,
    password: str = None,
    session=None,
):
    user = {
        "username": username,
        "email": email,
    }
    try:
        result = await db.user.insert_one(
            user,
            session=session,
        )
        user["_id"] = result.inserted_id

        if password != None:
            await setPassword(
                db=db,
                session=session,
                userID=user["_id"],
                password=password,
            )

        return user
    except DuplicateKeyError as err:
        parsedError = parseDuplicateKeyError(err)
        if parsedError.indexName == "uniqueEmail":
            raise ClientError(
                message=f"The email \"{email}\" is already in use",
                statusCode=422,
            )
        if parsedError.indexName == "uniqueUsername":
            raise ClientError(
                message=f"The username \"{username}\" is already in use",
                statusCode=422,
            )
        # unknown error
        raise err

    except Exception as err:
        raise err


class EmbeddedUserField(DictField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            fields={
                "_id": ObjectIdField(serializeTo="id"),
                "username": StringField(),
                # "email": StringField(),
            },
            *args,
            **kwargs,
        )
