from ..handler import Method, Endpoint, newMethod
from ..parsing import (
    RequestParser,
    DictParser,
    ResponseSerializerWithErrors,
)
from ..parsing.fields import (
    NonBlankStringField,
    EmailField,
    StringField,
    Field,
    DictField,
    ListField,
)

from ..schemas.user import createUser

from ..schemas.authentication import authenticateUser
from ..middleware import setCurrentUser

from ..errors import ServerError
import jwt
import datetime
import bson


class SignUpEndpoint(Endpoint):
    """
        Handle Initial account creation
    """

    name = "Sign Up"

    async def postProcess(
        self,
        email: str,
        username: str,
        password: str,
    ):

        user = await createUser(
            db=self.settings.db,
            username=username,
            email=email,
            password=password,
        )

        token = await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            user,
        )
        return {"success": "yes"}

    Post = newMethod(
        httpMethod="POST",
        description=
        "Create a new user with the given username, email, and password.",
        process=postProcess,
        bodyParameters={
            "email": EmailField(
                description="The email of the user being created"
            ),
            "username": NonBlankStringField(
                description="The username of the user being created"
            ),
            "password": NonBlankStringField(
                description="The password to set for the new user"
            ),
        },
        responseFields={
            "success": Field(
                description="A boolean of whether the user was created"
            ),
            "errors": ListField(DictField({})),
        }
    )


class LogInEndpoint(Endpoint):
    """
    Log in a user
    """
    name = "Log In"

    async def postProcess(
        self,
        email: str,
        password: str,
    ):
        user = await authenticateUser(
            db=self.settings.db,
            email=email,
            password=password,
        )
        token = await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            user,
        )

        return {
            "token": token,
            "currentUser": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
            },
        }

    Post = newMethod(
        httpMethod="POST",
        description="Log in the use with the given email and password",
        process=postProcess,
        bodyParameters={
            "email": EmailField(),
            "password": StringField(),
        },
        responseFields={
            "token": StringField(),
            "currentUser": DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            }),
            "errors": ListField(DictField({})),
        }
    )


class LogOutEndpoint(Endpoint):
    """
    Log out the Current User
    """

    name = "Log Out"

    async def process(self, ):
        self.unsetCookie("authentication", )
        return {}

    Get = newMethod(
        httpMethod="GET",
        description=
        "Log out the current user by unsetting the relevant cookies",
        process=process,
        responseFields={
            "errors": ListField(DictField({})),
        }
    )


class MeEndpoint(Endpoint):
    """
    Return information about the currently logged in user
    """

    name = "Me"

    async def processGet(self, currentUser):
        await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            currentUser,
        )
        return {
            "currentUser": {
                "id": str(currentUser["_id"]),
                "username": currentUser["username"],
                "email": currentUser["email"],
            },
        }

    Get = newMethod(
        httpMethod="GET",
        description="Return information about the currently logged in user",
        process=processGet,
        responseFields={
            "currentUser": DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            }),
            "errors": ListField(DictField({})),
        }
    )
