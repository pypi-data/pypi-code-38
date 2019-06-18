# -*- coding: utf-8 -*-
from guillotina.tests.utils import get_container


async def test_content(dbusers_requester):
    async with await dbusers_requester as requester:
        container = await get_container(requester)
        users = await container.async_get('users')
        assert users.type_name == 'UserManager'
        groups = await container.async_get('groups')
        assert groups.type_name == 'GroupManager'
