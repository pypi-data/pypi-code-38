from aiohttp import web

from unv.utils.files import calc_crc32_for_file

from .deploy import SETTINGS as DEPLOY_SETTINGS


async def render_template(
        request, template_name, context=None, status=web.HTTPOk.status_code):
    template = request.app['jinja2'].get_template(template_name)
    return web.Response(
        text=await template.render_async(context or {}),
        status=status, charset='utf-8',
        content_type='text/html'
    )


def url_for_static(path: str, private: bool = False, with_hash: bool = False):
    url = DEPLOY_SETTINGS.static_public_url
    directory = DEPLOY_SETTINGS.static_public_dir

    if private:
        url = DEPLOY_SETTINGS.static_private_url
        directory = DEPLOY_SETTINGS.static_private_dir

    real_path = directory / path.lstrip('/')
    hash_ = ''
    if with_hash:
        hash_ = '?hash={}'.format(calc_crc32_for_file(real_path))
    path = str(path).replace(str(directory), '', 1).lstrip('/')
    return f"{url}/{path}{hash_}"


def url_with_domain(path: str):
    protocol = 'http'
    path = path.lstrip('/')
    if DEPLOY_SETTINGS.use_https:
        protocol = 'https'
    return f'{protocol}://{DEPLOY_SETTINGS.domain}/{path}'


def make_url_for_func(app):
    def url_for(route, with_domain=False, **parts):
        parts = {key: str(value) for key, value in parts.items()}
        url = app.router[route].url_for(**parts)
        if with_domain:
            url = url_with_domain(url)
        return url
    return url_for


def inline_static_from(path, private=False):
    directory = DEPLOY_SETTINGS.static_public_dir
    if private:
        directory = DEPLOY_SETTINGS.static_private_dir

    with (directory / path).open('r') as f:
        return f.read().replace("\n", "")
