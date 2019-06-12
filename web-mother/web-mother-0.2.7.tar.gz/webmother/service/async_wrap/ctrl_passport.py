# coding:utf-8

from .. import ctrl_passport
from asyncio import get_event_loop


async def passport_create(cid, oid, passport_json, is_anon, *auth_args):
    args = cid, oid, passport_json, is_anon, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_passport.passport_create, *args)


async def passport_read(cid, oid):
    args = cid, oid
    return await get_event_loop().run_in_executor(None, ctrl_passport.passport_read, *args)


async def passport_update(cid, oid, passport_json, is_anon, *auth_args):
    args = cid, oid, passport_json, is_anon, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_passport.passport_update, *args)


async def passport_remove(cid, oid, *auth_args):
    args = cid, oid, *auth_args
    return await get_event_loop().run_in_executor(None, ctrl_passport.passport_remove, *args)


async def passports_query(cid):
    args = (cid,)
    return await get_event_loop().run_in_executor(None, ctrl_passport.passports_query, *args)
