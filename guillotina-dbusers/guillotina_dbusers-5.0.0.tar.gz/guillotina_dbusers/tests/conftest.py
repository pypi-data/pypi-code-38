from guillotina.testing import TESTING_SETTINGS
import json
import pytest


TESTING_SETTINGS.update(
    {
        "auth_user_identifiers": ["guillotina_dbusers.users.DBUserIdentifier"],
        "applications": ["guillotina_dbusers"],
    }
)


from guillotina.tests.conftest import *  # noqa
from guillotina.tests.utils import ContainerRequesterAsyncContextManager  # noqa


class DBUsersRequester(ContainerRequesterAsyncContextManager):
    async def __aenter__(self):
        requester = await super().__aenter__()
        await requester(
            "POST", "/db/guillotina/@addons", data=json.dumps({"id": "dbusers"})
        )
        return requester


@pytest.fixture(scope="function")
async def dbusers_requester(guillotina):
    return DBUsersRequester(guillotina)


@pytest.fixture
async def user_data():
    return {
        "@type": "User",
        "name": "Foobar",
        "id": "foobar",
        "username": "foobar",
        "email": "foo@bar.com",
        "password": "password",
    }
