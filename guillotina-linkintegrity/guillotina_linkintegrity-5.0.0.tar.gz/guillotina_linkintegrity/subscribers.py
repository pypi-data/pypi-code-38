import os

from guillotina import configure
from guillotina.component import get_utility
from guillotina.contrib.catalog.pg import sqlq
from guillotina.exceptions import ContainerNotFound
from guillotina.interfaces import ICacheUtility
from guillotina.interfaces import IObjectMovedEvent
from guillotina.interfaces import IResource
from guillotina.interfaces import ITraversalMissEvent
from guillotina.response import HTTPMovedPermanently
from guillotina.utils import execute
from guillotina.utils import find_container
from guillotina.utils import get_content_path
from guillotina.utils import get_current_container
from guillotina.utils import get_object_by_oid
from guillotina.utils import get_object_url
from guillotina_linkintegrity import utils
from pypika import PostgreSQLQuery as Query
from pypika import Table


aliases_table = Table('aliases')


@configure.subscriber(for_=(IResource, IObjectMovedEvent))
async def object_moved(ob, event):
    parent_path = get_content_path(event.old_parent)
    old_path = os.path.join(parent_path, event.old_name)
    storage = utils.get_storage()
    container = find_container(ob)
    execute.after_request(
        utils.add_aliases, ob, [old_path], moved=True,
        container=container, storage=storage)
    cache = get_utility(ICacheUtility)
    execute.after_request(
        cache.send_invalidation,
        ['{}-id'.format(ob.__uuid__),
         '{}-links'.format(ob.__uuid__),
         '{}-links-to'.format(ob.__uuid__)])


@configure.subscriber(for_=ITraversalMissEvent)
async def check_content_moved(event):
    request = event.request
    try:
        get_current_container()
    except ContainerNotFound:
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
        (aliases_table.path == sqlq(path)) |
        (aliases_table.path == sqlq(path) + '/' + sqlq(view))
    )

    async with storage.pool.acquire() as conn:
        results = await conn.fetch(str(query))

    if len(results) > 0:
        ob = await get_object_by_oid(results[0]['zoid'])
        url = get_object_url(ob)
        if view:
            url += '/' + view
        raise HTTPMovedPermanently(url)
