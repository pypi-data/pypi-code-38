from typing import Optional

import pytest

from anji_orm import Field, orm_register
from asynctest.mock import CoroutineMock

from sanic_service_utils.orm_utils import DataTableMixin


orm_register.init('rethinkdb://', {}, async_mode=True)


class T1(DataTableMixin):
    _table = 'c1'

    c1: Optional[str] = Field(secondary_index=True)
    c2: Optional[str]


class MockRecord:

    async def convert_to_web_info(self):
        return {"dummy": "info"}


class MockRequest:

    def __init__(self, args):
        self.args = args


@pytest.mark.parametrize("request_args,required_query", [
    ({}, T1.all())
])
@pytest.mark.asyncio
async def test_orm_request(mocker, request_args, required_query):
    async_run = mocker.patch(
        'anji_orm.core.ast.base.QueryAst.async_run',
        return_value=[MockRecord(), MockRecord()],
        new_callable=CoroutineMock
    )

    await T1.process_web_request(MockRequest(request_args))
    assert async_run.call_count == 2
