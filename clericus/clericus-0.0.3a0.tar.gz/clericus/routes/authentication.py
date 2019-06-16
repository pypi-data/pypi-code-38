from ..handler import Method, Endpoint
from ..parsing import (
    RequestParser,
    DictParser,
    ResponseSerializerWithErrors,
)
from ..parsing.fields import (
    NonBlankStringField,
    EmailField,
    StringField,
    JwtField,
    Field,
    DictField,
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

    class Post(Method):
        """
            Create a new user with the given username, email, and password.
        """

        class Parser(RequestParser):
            class BodyParser(DictParser):
                email = EmailField(
                    description="The email of the user being created"
                )
                username = NonBlankStringField(
                    description="The username of the user being created"
                )
                password = NonBlankStringField(
                    description="The password to set for the new user"
                )

        class Serializer(ResponseSerializerWithErrors):
            def __init__(self):
                self.success = Field(
                    description="A boolean of whether the user was created"
                )

        async def process(
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


class LogInEndpoint(Endpoint):
    class Post(Method):
        class Parser(RequestParser):
            class BodyParser(DictParser):
                email = EmailField()
                password = StringField()

        class Serializer(ResponseSerializerWithErrors):
            token = StringField()
            currentUser = DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            })

        async def process(
            self,
            email: str,
            password: str,
            # currentUser=None,
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


class LogOutEndpoint(Endpoint):
    class Get(Method):

        # class Serializer(ResponseSerializerWithErrors):
        #     def __init__(self):
        #         self.token = StringField()

        async def process(
            self,
            authenticated: str = None,
        ):

            self.unsetCookie("authentication", )
            return {}


class MeEndpoint(Endpoint):
    class Get(Method):
        class Serializer(ResponseSerializerWithErrors):
            currentUser = DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            })

        async def process(self, currentUser):
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
