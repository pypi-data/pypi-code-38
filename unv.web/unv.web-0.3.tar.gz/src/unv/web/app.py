import os
import inspect

import uvloop
import jinja2
import asyncio

from pathlib import Path

from aiohttp import web

from unv.app.base import Application
from unv.app.settings import SETTINGS as APP_SETTINGS

from .helpers import (
    url_for_static, url_with_domain, inline_static_from, make_url_for_func
)
from .deploy import SETTINGS as DEPLOY_SETTINGS
from .settings import SETTINGS


def setup_event_loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    if APP_SETTINGS.is_development:
        loop.set_debug(True)


def setup_jinja2(app: web.Application):
    if not SETTINGS.jinja2_enabled:
        return

    app['jinja2'] = jinja2.Environment(**SETTINGS.jinja2_settings)
    print('settings', SETTINGS.jinja2_settings)
    app['jinja2'].globals.update({
        'url_for': make_url_for_func(app),
        'url_for_static': url_for_static,
        'url_with_domain': url_with_domain,
        'inline_static_from': inline_static_from,
        'for_developemnt': APP_SETTINGS.is_development,
        'for_production': APP_SETTINGS.is_production,
        'for_testing': APP_SETTINGS.is_testing
    })


def setup_static_dirs(app: Application):
    if not SETTINGS.link_static:
        return

    for component in app.components:
        component_path = Path(inspect.getfile(component)).parent
        static_path = component_path / 'static'
        public_dir = DEPLOY_SETTINGS.static_public_dir
        private_dir = DEPLOY_SETTINGS.static_private_dir

        public_app_dir = static_path / public_dir.name
        for directory in public_app_dir.glob('*'):
            os.system('mkdir -p {}'.format(public_dir))
            os.system('ln -sf {} {}'.format(directory, public_dir))

        private_app_dir = static_path / private_dir.name
        for directory in private_app_dir.glob('*'):
            os.system('mkdir -p {}'.format(private_dir))
            os.system('ln -sf {} {}'.format(directory, private_dir))


def run_web_app_task(app: web.Application):
    web.run_app(
        app,
        host=DEPLOY_SETTINGS.host,
        port=DEPLOY_SETTINGS.port + DEPLOY_SETTINGS.instance,
        access_log=None
    )


def setup(app: Application):
    app.register(web.Application())
    app.register_setup_task(setup_event_loop)
    app.register_setup_task(setup_jinja2)
    app.register_setup_task(setup_static_dirs)
    app.register_run_task(run_web_app_task)
