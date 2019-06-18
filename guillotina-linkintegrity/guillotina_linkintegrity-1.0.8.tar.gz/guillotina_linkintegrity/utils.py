import logging
import os
import string

from guillotina.db.interfaces import IPostgresStorage
from guillotina.interfaces import IContainer
from guillotina.transactions import get_transaction
from guillotina.utils import get_content_path
from guillotina.utils import get_current_request
from guillotina.utils import get_object_url
from guillotina_linkintegrity.cache import cached_wrapper
from guillotina_linkintegrity.cache import invalidate_wrapper
from lxml import html
from pypika import PostgreSQLQuery as Query
from pypika import Table


logger = logging.getLogger(__name__)
aliases_table = Table('aliases')
links_table = Table('links')
objects_table = Table('objects')


def _safe_uid(uid):
    return ''.join([l for l in uid
                    if l in string.ascii_letters + string.digits + '|'])


def get_storage():
    txn = get_transaction()
    storage = txn.manager._storage
    if not IPostgresStorage.providedBy(storage):
        # would already get big warning log about this
        logger.debug('Storage does not support link integrity')
        return None
    return storage


@cached_wrapper('aliases')
async def get_aliases(ob, storage=None) -> list:
    storage = storage or get_storage()
    if storage is None:
        return
    query = Query.from_(aliases_table).select(
        aliases_table.path, aliases_table.moved
    ).where(
        aliases_table.zoid == _safe_uid(ob._p_oid)
    )
    async with storage.pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append({
            'path': result['path'],
            'moved': result['moved']
        })
    return data


@invalidate_wrapper(['aliases'])
async def add_aliases(ob, paths: list, container=None, moved=True,
                      storage=None):
    if not isinstance(moved, bool):
        raise Exception('Invalid type {}'.format(moved))

    storage = storage or get_storage()
    if storage is None:
        return

    if container is None:
        req = get_current_request()
        container = req.container
    query = Query.into(aliases_table).columns(
        'zoid', 'container_id', 'path', 'moved')
    values = []
    for i, path in enumerate(paths):
        if not isinstance(path, str):
            raise Exception('Invalid type {}'.format(path))
        path = '/' + path.strip('/')
        values.append(path)
        query = query.insert(
            ob._p_oid,
            container._p_oid,
            f'${i + 1}',
            moved,
        )

    query = str(query)
    for i in range(len(paths)):
        query = query.replace(f"'${i + 1}'", f"${i + 1}")
    async with storage.pool.acquire() as conn:
        await conn.execute(query, *values)


@invalidate_wrapper(['aliases'])
async def remove_aliases(ob, paths: list, storage=None):
    storage = storage or get_storage()
    if storage is None:
        return

    for path in paths:
        query = Query.from_(aliases_table).where(
            (aliases_table.zoid == _safe_uid(ob._p_oid)) &
            (aliases_table.path == '$1')
        )
        async with storage.pool.acquire() as conn:
            await conn.execute(
                str(query.delete()).replace("'$1'", "$1"),
                path)


async def get_inherited_aliases(ob) -> list:
    storage = get_storage()
    if storage is None:
        return []

    ob_path = get_content_path(ob)
    data = []
    context = ob.__parent__
    while context is not None and not IContainer.providedBy(context):
        context_path = get_content_path(context)
        for alias in await get_aliases(context):
            if not alias['moved']:
                continue
            path = alias['path']
            current_sub_path = ob_path[len(context_path):]
            path = os.path.join(path, current_sub_path.strip('/'))
            alias['context_path'] = context_path
            alias['path'] = path
            data.append(alias)
        context = context.__parent__

    return data


@cached_wrapper('links')
async def get_links(ob) -> list:
    storage = get_storage()
    if storage is None:
        return []

    query = Query.from_(links_table).select(
        links_table.target_id
    ).where(
        links_table.source_id == _safe_uid(ob._p_oid)
    )
    async with storage.pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append(result['target_id'])
    return data


@cached_wrapper('links-to')
async def get_links_to(ob) -> list:
    storage = get_storage()
    if storage is None:
        return []

    query = Query.from_(links_table).select(
        links_table.source_id
    ).where(
        links_table.target_id == _safe_uid(ob._p_oid)
    )
    async with storage.pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append(result['source_id'])
    return data


@invalidate_wrapper(['links'], ['links-to'])
async def add_links(ob, links):
    storage = get_storage()
    if storage is None:
        return

    query = Query.into(links_table).columns('source_id', 'target_id')
    for link in links:
        query = query.insert(
            _safe_uid(str(ob._p_oid)), _safe_uid(str(link._p_oid)))
    async with storage.pool.acquire() as conn:
        await conn.execute(str(query))


@invalidate_wrapper(['links'], ['links-to'])
async def remove_links(ob, links):
    storage = get_storage()
    if storage is None:
        return

    query = Query.from_(links_table).where(
        (links_table.source_id == _safe_uid(ob._p_oid)) &
        links_table.target_id.isin([_safe_uid(l._p_oid) for l in links])
    )
    async with storage.pool.acquire() as conn:
        await conn.execute(str(query.delete()))


@invalidate_wrapper(['links'], ['links-to'])
async def update_links_from_html(ob, *contents):
    storage = get_storage()
    if storage is None:
        return

    links = set()
    for content in contents:
        dom = html.fromstring(content)
        for node in dom.xpath('//a') + dom.xpath('//img'):
            url = node.get('href', node.get('src', ''))
            if 'resolveuid/' not in url:
                continue
            _, _, uid = url.partition('resolveuid/')
            uid = uid.split('/')[0].split('?')[0]
            links.add(_safe_uid(uid))

    if len(links) == 0:
        # delete existing if there are any
        async with storage.pool.acquire() as conn:
            await conn.execute(str(Query.from_(links_table).where(
                links_table.source_id == _safe_uid(ob._p_oid)
            ).delete()))
        return

    async with storage.pool.acquire() as conn:
        # make sure to filter out bad links
        existing_oids = set()
        query = str(
            Query.from_(objects_table).select('zoid').where(
                objects_table.zoid == '$1'
            )).replace("'$1'", "any($1)")
        results = await conn.fetch(query, list(links))
        for record in results:
            existing_oids.add(record['zoid'])

        # first delete all existing ones
        await conn.execute(str(Query.from_(links_table).where(
            links_table.source_id == ob._p_oid
        ).delete()))

        # then, readd
        links = links & existing_oids
        if len(links) > 0:
            query = Query.into(links_table).columns('source_id', 'target_id')
            for link in links:
                query = query.insert(
                    _safe_uid(str(ob._p_oid)), _safe_uid(link))

            await conn.execute(str(query))


@cached_wrapper('id', ob_key=False)
async def _get_id(zoid):
    storage = get_storage()
    if storage is None:
        return
    async with storage.pool.acquire() as conn:
        result = await conn.fetch(str(
            Query.from_(objects_table).select(
                'id', 'parent_id').where(
                    objects_table.zoid == _safe_uid(zoid))))
    if len(result) > 0:
        return {
            'id': result[0]['id'],
            'parent': result[0]['parent_id']
        }
    # could not find, this should not happen


async def translate_links(content, container=None) -> str:
    '''
    optimized url builder here so we don't pull
    full objects from database however, we lose caching.

    Would be great to move this into an implementation
    that worked with current cache/invalidation strategies
    '''

    req = None
    if container is None:
        req = get_current_request()
        container = req.container
    container_url = get_object_url(container, req)
    dom = html.fromstring(content)
    contexts = {}

    for node in dom.xpath('//a') + dom.xpath('//img'):
        url = node.get('href', node.get('src', ''))
        if 'resolveuid/' not in url:
            continue
        path = []
        _, _, current_uid = url.partition('resolveuid/')
        current_uid = current_uid.split('/')[0].split('?')[0]

        error = False
        while current_uid != container._p_oid:
            if current_uid not in contexts:
                # fetch from db
                result = await _get_id(current_uid)
                if result is not None:
                    contexts[current_uid] = result
                else:
                    # could not find, this should not happen
                    error = True
                    break
            path = [contexts[current_uid]['id']] + path
            current_uid = contexts[current_uid]['parent']

        if error:
            continue
        url = os.path.join(container_url, '/'.join(path))
        attr = node.tag.lower() == 'a' and 'href' or 'src'
        node.attrib[attr] = url

    return html.tostring(dom).decode('utf-8')
