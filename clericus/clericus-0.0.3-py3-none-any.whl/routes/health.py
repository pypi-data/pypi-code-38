from ..handler import Method, Endpoint
from ..parsing import (
    RequestParser,
    DictParser,
    ResponseSerializer,
)
from ..parsing.fields import (
    NonBlankStringField,
    EmailField,
    StringField,
    JwtField,
    Field,
)

from ..errors import ServerError
import jwt
import datetime


class HealthCheckEndpoint(Endpoint):
    """
        Return the status of the server
    """

    class Get(Method):
        """
            Return the status of the server
        """


        class Serializer(ResponseSerializer):
            def __init__(self):
                self.healthy = Field(
                    description="A boolean of whether the server is healthy",
                    default=True,
                )

        async def process(
            self,
        ):
            try:
                resp = await self.settings.db.command("ping")

                return {"healthy": True}
            except Exception as e:
                print(e)
                raise ServerError(message="Server is unhealthy")
