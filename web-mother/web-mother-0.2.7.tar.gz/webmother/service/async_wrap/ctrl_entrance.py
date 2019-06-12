# coding:utf-8

from .. import ctrl_entrance
from asyncio import get_event_loop


async def query_employments(oid, uid, access_token):
    args = oid, uid, access_token
    return await get_event_loop().run_in_executor(None, ctrl_entrance.query_employments, *args)


async def employ_passports(system, *auth_args):
    args = system, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_entrance.employ_passports, *args)


async def query_customer_passports(system, oid, uid, access_token):
    args = system, oid, uid, access_token
    return await get_event_loop().run_in_executor(None, ctrl_entrance.query_customer_passports, *args)
