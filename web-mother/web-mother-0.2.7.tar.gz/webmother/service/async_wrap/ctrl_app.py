# coding:utf-8

from .. import ctrl_app
from asyncio import get_event_loop


async def open_customer_org(oid, data, *auth_args):
    args = oid, data, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_app.open_customer_org, *args)


async def close_customer_org(oid, *auth_args):
    args = oid, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_app.close_customer_org, *args)

