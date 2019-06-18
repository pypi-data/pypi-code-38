import json


async def test_redirect_after_content_renamed(container_requester):
    async with container_requester as requester:
        await requester('POST', '/db/guillotina', data=json.dumps({
            'id': 'foobar',
            '@type': 'Item'
        }))
        await requester('POST', '/db/guillotina/foobar/@move',
                        data=json.dumps({
                            'new_id': 'foobar2'
                        }))
        _, status = await requester(
            'GET', '/db/guillotina/foobar', allow_redirects=False)
        assert status == 301

        _, status = await requester(
            'GET', '/db/guillotina/foobar/@ids', allow_redirects=False)
        assert status == 301


async def test_api_aliases(container_requester):
    async with container_requester as requester:
        await requester('POST', '/db/guillotina', data=json.dumps({
            'id': 'foo',
            '@type': 'Folder'
        }))
        await requester('POST', '/db/guillotina/foo', data=json.dumps({
            'id': 'bar',
            '@type': 'Item'
        }))
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0

        await requester(
            'PATCH', '/db/guillotina/foo/@aliases',
            data=json.dumps({
                'paths': ['/foo2']
            }))
        await requester(
            'PATCH', '/db/guillotina/foo/bar/@aliases',
            data=json.dumps({
                'paths': ['/foobar']
            }))

        resp, _ = await requester('GET', '/db/guillotina/foo/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 1

        # not from move so should *not* inherit
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 1

        await requester(
            'DELETE', '/db/guillotina/foo/@aliases',
            data=json.dumps({
                'paths': ['/foo2']
            }))
        await requester(
            'DELETE', '/db/guillotina/foo/bar/@aliases',
            data=json.dumps({
                'paths': ['/foobar']
            }))

        resp, _ = await requester('GET', '/db/guillotina/foo/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0

        # not from move so should *not* inherit
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0
