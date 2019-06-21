from ..handler import Method, Endpoint, newMethod
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
    BoolField,
    Field,
)

from ..errors import ServerError
import jwt
import datetime


class HealthCheckEndpoint(Endpoint):
    """
        Return the status of the server
    """
    name = "Health Check"

    async def getProcess(self, ):
        try:
            resp = await self.settings.db.command("ping")

            return {"healthy": True}
        except Exception as e:
            print(e)
            raise ServerError(message="Server is unhealthy")

    Get = newMethod(
        httpMethod="Get",
        description="""Return the status of the server""",
        process=getProcess,
        responseFields={
            "healthy": Field(
                description="A boolean of whether the server is healthy",
                default=True,
            )
        }
    )
