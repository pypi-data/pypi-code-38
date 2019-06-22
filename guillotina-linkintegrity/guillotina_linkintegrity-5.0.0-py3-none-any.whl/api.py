from guillotina import configure
from guillotina.interfaces import IResource
from guillotina.utils import find_container
from guillotina_linkintegrity import utils


@configure.service(method='GET', name='@aliases', context=IResource,
                   permission='guillotina.AccessContent')
async def get_aliases(context, request):
    return {
        'inherited': await utils.get_inherited_aliases(context),
        'aliases': await utils.get_aliases(context)
    }


@configure.service(method='PATCH', name='@aliases', context=IResource,
                   permission='guillotina.ModifyContent')
async def patch_aliases(context, request):
    data = await request.json()
    container = find_container(context)
    await utils.add_aliases(
        context, data['paths'], container=container, moved=False)
    return {}


@configure.service(method='DELETE', name='@aliases', context=IResource,
                   permission='guillotina.ModifyContent')
async def delete_aliases(context, request):
    data = await request.json()
    await utils.remove_aliases(context, data['paths'])
    return {}


@configure.service(method='GET', name='@links', context=IResource,
                   permission='guillotina.ModifyContent')
async def get_links(context, request):
    return await utils.get_links(context)


@configure.service(method='GET', name='@links-to', context=IResource,
                   permission='guillotina.ModifyContent')
async def get_links_to(context, request):
    return await utils.get_links_to(context)
