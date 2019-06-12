# coding:utf-8

from .. import ctrl_catalog
from asyncio import get_event_loop


async def create(cid, data, *auth_args):
    args = (cid, data, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_catalog.create, *args)


async def read(cid, *auth_args):
    args = (cid, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_catalog.read, *args)


async def update(cid, data, *auth_args):
    args = cid, data, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_catalog.update, *args)


async def change_status(cid, action, *auth_args):
    args = cid, action, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_catalog.change_status, *args)


async def children(cid, *auth_args):
    args = cid, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_catalog.children, *args)


async def move(cid, cid_to, *auth_args):
    args = cid, cid_to, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_catalog.move, *args)
