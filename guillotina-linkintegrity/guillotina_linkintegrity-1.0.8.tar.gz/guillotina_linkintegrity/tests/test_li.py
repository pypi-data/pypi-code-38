from guillotina.content import create_content_in_container
from guillotina_linkintegrity import utils


async def test_add_alias(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            foobar = await create_content_in_container(
                container, 'Item', id_='foobar')
            await txn.commit()  # writes out content
            await utils.add_aliases(
                foobar, ['/foobar2'], container=container)

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/foobar2'


async def test_remove_alias(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            foobar = await create_content_in_container(
                container, 'Item', id_='foobar')
            await txn.commit()  # writes out content
            await utils.add_aliases(
                foobar, ['/foobar2'], container=container)
            await utils.add_aliases(
                foobar, ['/foobar3'], container=container)

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 2

            await utils.remove_aliases(foobar, ['/foobar2'])

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/foobar3'


async def test_get_inherited_aliases(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            item = await create_content_in_container(
                folder, 'Item', id_='item')
            await txn.commit()  # writes out content
            await utils.add_aliases(
                folder, ['/other'], container=container)

            assert len(await utils.get_aliases(folder)) == 1
            assert len(await utils.get_aliases(item)) == 0

            aliases = await utils.get_inherited_aliases(item)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/other/item'


async def test_add_links(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            item1 = await create_content_in_container(
                folder, 'Item', id_='item1')
            item2 = await create_content_in_container(
                folder, 'Item', id_='item2')

            await txn.commit()  # writes out content
            await utils.add_links(folder, [item1, item2])

            assert len(await utils.get_links(folder)) == 2


async def test_remove_links(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            item1 = await create_content_in_container(
                folder, 'Item', id_='item1')
            item2 = await create_content_in_container(
                folder, 'Item', id_='item2')

            await txn.commit()  # writes out content
            await utils.add_links(folder, [item1, item2])

            assert len(await utils.get_links(folder)) == 2

            await utils.remove_links(folder, [item1, item2])
            assert len(await utils.get_links(folder)) == 0


async def test_update_links_from_html(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            item1 = await create_content_in_container(
                folder, 'Item', id_='item1')
            item2 = await create_content_in_container(
                folder, 'Item', id_='item2')
            item3 = await create_content_in_container(
                folder, 'Item', id_='item3')
            await txn.commit()  # writes out content

            html = f'''<p>
<a href="@resolveuid/{item1._p_oid}">item1</a>
<a href="@resolveuid/{item2._p_oid}">item1</a>
<a href="@resolveuid/{item3._p_oid}">item1</a>
<img src="@resolveuid/{item3._p_oid}" />
</p>'''
            await utils.update_links_from_html(folder, html)

            assert len(await utils.get_links(folder)) == 3

            html = f'''<p>
<a href="@resolveuid/{item1._p_oid}">item1</a>
</p>'''
            await utils.update_links_from_html(folder, html)
            assert len(await utils.get_links(folder)) == 1


async def test_update_links_from_html_ignore_invalid(
        guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')

            item1 = await create_content_in_container(
                folder, 'Item', id_='item1')
            await txn.commit()  # writes out content

            html = f'''<p>
<a href="@resolveuid/{item1._p_oid}">item1</a>
<a href="@resolveuid/foobar-expired">item1</a>
</p>'''
            await utils.update_links_from_html(folder, html)
            assert len(await utils.get_links(folder)) == 1


async def test_translate_html(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            folder2 = await create_content_in_container(
                folder, 'Folder', id_='folder2')
            folder3 = await create_content_in_container(
                folder2, 'Folder', id_='folder3')
            folder4 = await create_content_in_container(
                folder3, 'Folder', id_='folder4')

            await txn.commit()  # writes out content

            html = f'''<p>
<a href="@resolveuid/{folder4._p_oid}">item1</a>
<a href="@resolveuid/{folder3._p_oid}">item1</a>

</p>'''
            result = await utils.translate_links(html, container)
            assert '/folder/folder2/folder3/folder4"' in result
            assert '/folder/folder2/folder3"' in result
