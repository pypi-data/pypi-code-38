# coding:utf-8

from .. import ctrl_org
from asyncio import get_event_loop


async def create(oid, data, *auth_args):
    args = (oid, data, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_org.create, *args)


async def read(oid, *auth_args):
    args = (oid, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_org.read, *args)


async def update(oid, data, *auth_args):
    args = oid, data, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_org.update, *args)


async def change_status(oid, action, *auth_args):
    args = oid, action, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_org.change_status, *args)


async def children(oid, *auth_args):
    args = (oid, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_org.children, *args)


async def move(oid, oid_to, *auth_args):
    args = oid, oid_to, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_org.move, *args)
