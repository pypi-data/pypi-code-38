# coding:utf-8

from .. import ctrl_person
from asyncio import get_event_loop


async def add(oid, indicator, identity_json, *auth_args):
    args = oid, indicator, identity_json, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_person.add, *args)


async def get(oid, uid, *auth_args):
    args = oid, uid, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_person.get, *args)


async def update(oid, uid, mmb_meta, *auth_args):
    args = oid, uid, mmb_meta, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_person.update, *args)


async def remove(oid, uid, *auth_args):
    args = oid, uid, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_person.remove, *args)


async def query(oid, page_no, page_size, *auth_args):
    args = (oid, page_no, page_size, *auth_args)
    return await get_event_loop().run_in_executor(None, ctrl_person.query, *args)
