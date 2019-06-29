import aiobotocore

from botocore.session import Session
from pyapp.conf.helpers import ThreadLocalNamedSingletonFactory

__all__ = ("Session", "session_factory", "create_client")


class SessionFactory(ThreadLocalNamedSingletonFactory[Session]):
    """
    Factory for creating AWS sessions.
    """

    defaults = {
        "region_name": None,
        "aws_access_key_id": None,
        "aws_secret_access_key": None,
        "aws_session_token": None,
    }

    def create(self, name: str = None) -> Session:
        config = self.get(name)
        session = aiobotocore.get_session()

        if config["region_name"]:
            session.set_config_variable("region", config["region_name"])

        if (
            config["aws_access_key_id"]
            or config["aws_secret_access_key"]
            or config["aws_session_token"]
        ):
            session.set_credentials(
                config["aws_access_key_id"],
                config["aws_secret_access_key"],
                config["aws_session_token"],
            )

        return session


session_factory = SessionFactory("AWS_CREDENTIALS")


def create_client(service_name: str, config_name: str = None):
    """
    Factory for creating AWS clients.
    """
    session = session_factory.create(config_name)
    return session.create_client(service_name)
