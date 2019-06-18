import yarl
import logging
from aiohttp import web
from guillotina import api, app_settings, configure
from guillotina.auth import authenticate_user
from guillotina.event import notify
from guillotina.events import UserLogin
from guillotina.interfaces import IApplication, IContainer
from guillotina.response import HTTPBadRequest, HTTPFound, HTTPNotFound
from guillotina.api.login import Refresh as GuillotinaRefresh
from guillotina_authentication import cache, exceptions, utils

http_exception_mappings = {
    exceptions.ProviderNotSupportedException: (
        HTTPNotFound, '{provider} is not supported'),
    exceptions.ProviderNotConfiguredException: (
        HTTPNotFound, '{provider} is not configured'),
    exceptions.ProviderMisConfiguredException: (
        HTTPNotFound, '{provider} is misconfigured'),
}


logger = logging.getLogger(__name__)


@configure.service(context=IApplication, method='GET',
                   name='@authentication-providers', allow_access=True)
@configure.service(context=IContainer, method='GET',
                   name='@authentication-providers', allow_access=True)
async def auth_providers(context, request):
    return list(set(
        app_settings['auth_providers']) & set(utils.config_mappings.keys()))


@configure.service(context=IApplication, method='GET',
                   name='@authenticate/{provider}', allow_access=True,
                   parameters=[{
                        'in': 'query',
                        'name': 'scope',
                        'description': 'scape separated list'
                   }])
@configure.service(context=IContainer, method='GET',
                   name='@authenticate/{provider}', allow_access=True,
                   parameters=[{
                        'in': 'query',
                        'name': 'scope',
                        'description': 'scape separated list'
                   }])
async def auth(context, request):
    provider = request.matchdict['provider']
    try:
        client = utils.get_client(provider)
    except exceptions.AuthenticationException as exc:
        if type(exc) in http_exception_mappings:
            ExcType, reason = http_exception_mappings[type(exc)]
            raise ExcType(content={
                'reason': reason.format(provider=provider)
            })
    if 'callback' not in request.url.query:
        callback_url = str(request.url.with_path('@callback/' + provider))
    else:
        callback_url = request.url.query['callback']
    return HTTPFound(await utils.get_authentication_url(
        client, callback=callback_url,
        scope=request.url.query.get('scope') or ''))


@configure.service(context=IApplication, method='GET',
                   name='@authorize/{provider}', allow_access=True,
                   parameters=[{
                        'in': 'query',
                        'name': 'scope',
                        'description': 'scape separated list'
                   }])
@configure.service(context=IContainer, method='GET',
                   name='@authorize/{provider}', allow_access=True,
                   parameters=[{
                        'in': 'query',
                        'name': 'scope',
                        'description': 'scape separated list'
                   }])
async def authorize(context, request):
    provider = request.matchdict['provider']
    try:
        client = utils.get_client(provider)
    except exceptions.AuthenticationException as exc:
        if type(exc) in http_exception_mappings:
            ExcType, reason = http_exception_mappings[type(exc)]
            raise ExcType(content={
                'reason': reason.format(provider=provider)
            })
    callback_url = str(request.url.with_path('@callback/' + provider))
    return HTTPFound(await utils.get_authorization_url(
        client, callback=callback_url,
        scope=request.url.query.get('scope') or ''),
        access_type='offline')


@configure.service(context=IApplication, method='GET',
                   name='@callback/{provider}', allow_access=True)
@configure.service(context=IContainer, method='GET',
                   name='@callback/{provider}', allow_access=True)
async def auth_callback(context, request):
    provider = request.matchdict['provider']

    if provider in utils.oauth1_providers:
        oauth_verifier = request.url.query.get('oauth_verifier')
        oauth_token = request.url.query.get('oauth_token')
        client = utils.get_client(provider, oauth_token=oauth_token)
        request_token = await cache.get(oauth_token)
        if request_token is None:
            raise web.HTTPBadRequest(
                reason='Failed to obtain proper request token.')
        oauth_token, oauth_token_secret, otoken_data = await client.get_access_token(  # noqa
            oauth_verifier, oauth_token)

        client_args = dict(
            oauth_token=oauth_token,
            oauth_token_secret=oauth_token_secret)
    else:
        client = utils.get_client(provider)
        if 'error' in request.url.query:
            raise HTTPBadRequest(content=dict(request.url.query))

        if 'code' not in request.url.query:
            raise HTTPBadRequest(content=dict(request.url.query))

        code = request.url.query['code']

        if 'callback' not in request.url.query:
            callback = str(request.url.with_path('@callback/' + provider))
        else:
            callback = request.url.query['callback']

        forwarded_proto = request.headers.get('X-Forwarded-Proto', None)
        if forwarded_proto and forwarded_proto != request.scheme:
            callback = callback.replace(
                request.scheme + '://', forwarded_proto + '://')

        otoken, otoken_data = await client.get_access_token(
            code, redirect_uri=callback)

        client_args = dict(
            access_token=otoken,
            refresh_token=otoken_data['refresh_token'])

    if 'expires_in' in otoken_data:
        timeout = otoken_data['expires_in']
    else:
        timeout = 60 * 60 * 1

    client = utils.get_client(provider, **client_args)
    user, user_data = await client.user_info()

    jwt_token, data = authenticate_user(user.id, {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'username': user.username,
        'client': provider,
        'client_args': client_args,
        'allowed_scopes': user_data.get('allowed_scopes'),
        'scope': request.url.query.get('scope').split(' '),
        'identifier': 'oauth'
    }, timeout=timeout)

    await notify(UserLogin(user, jwt_token))

    result = {
        'exp': data['exp'],
        'token': jwt_token
    }
    if app_settings.get('auth_callback_url'):
        url = yarl.URL(
            app_settings['auth_callback_url']).with_query(result)
        return HTTPFound(str(url))
    return result


@configure.service(
    context=IApplication, method='GET', allow_access=True,
    permission='guillotina.AccessContent', name='@user',
    summary='Get information on the currently logged in user')
async def user_info(context, request):
    return await api.user.get_user_info(context, request)
