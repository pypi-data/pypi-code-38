import os

from guillotina import configure
from guillotina.interfaces import IObjectMovedEvent
from guillotina.interfaces import IResource
from guillotina.interfaces import ITraversalMissEvent
from guillotina.response import HTTPMovedPermanently
from guillotina.utils import execute
from guillotina.utils import get_content_path
from guillotina.utils import get_current_request
from guillotina.utils import get_object_by_oid
from guillotina.utils import get_object_url
from guillotina_linkintegrity import utils
from guillotina_linkintegrity.cache import get_cache
from pypika import PostgreSQLQuery as Query
from pypika import Table


aliases_table = Table('aliases')


@configure.subscriber(for_=(IResource, IObjectMovedEvent))
async def object_moved(ob, event):
    req = get_current_request()
    parent_path = get_content_path(event.old_parent)
    old_path = os.path.join(parent_path, event.old_name)
    storage = utils.get_storage()
    execute.after_request(
        utils.add_aliases, ob, [old_path], moved=True,
        container=req.container, storage=storage)
    cache = get_cache()
    execute.after_request(
        cache.publish_invalidation,
        '{}-id'.format(ob._p_oid),
        '{}-links'.format(ob._p_oid),
        '{}-links-to'.format(ob._p_oid))


@configure.subscriber(for_=ITraversalMissEvent)
async def check_content_moved(event):
    request = event.request
    if getattr(request, 'container', None) is None:
        return

    storage = utils.get_storage()
    if storage is None:
        return

    tail, _, view = '/'.join(event.tail).partition('/@')
    if view:
        view = '@' + view
    path = os.path.join(
        get_content_path(request.resource), tail)

    query = Query.from_(aliases_table).select(
        aliases_table.zoid
    ).where(
        (aliases_table.path == path) |
        (aliases_table.path == path + '/' + view)
    )

    async with storage.pool.acquire() as conn:
        results = await conn.fetch(str(query))

    if len(results) > 0:
        ob = await get_object_by_oid(results[0]['zoid'])
        url = get_object_url(ob)
        if view:
            url += '/' + view
        raise HTTPMovedPermanently(url)
