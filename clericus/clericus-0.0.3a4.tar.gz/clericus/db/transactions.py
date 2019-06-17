def withSession(f):
    async def wrapper(*args, db=None, session=None, **kwargs):
        if not session:
            async with await db.client.start_session() as session:
                async with session.start_transaction():
                    return await f(*args, db=db, session=session, **kwargs)

        return await f(*args, db=db, session=session, **kwargs)

    return wrapper