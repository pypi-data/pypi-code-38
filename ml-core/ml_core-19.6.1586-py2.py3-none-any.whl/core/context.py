# -*- coding: utf-8 -*-


class Expando(object):
    pass


def create_empty_context():
    return Expando()


def build_context(http_session, output_format=None, config_prefix=None, config_file=None):
    ctx = create_empty_context()

    init_context2(ctx, http_session, output_format, config_prefix, config_file)

    return ctx


def build_context_from_config(ctx, http_session, config):
    ctx.obj = Expando()

    ctx.obj.config = config
    ctx.obj.session = http_session


def init_context2(ctx, http_session, output_format=None, config_prefix=None, config_file=None):
    from .config import Config

    config = Config(config_prefix, config_file)

    build_context_from_config(ctx, http_session, config)

    ctx.obj.output_format = output_format

    ctx.obj.api_host = config.api_host
    ctx.obj.host = config.host
    ctx.obj.refresh_token = config.refresh_token

    ctx.obj.refresh_token = config.refresh_token
    ctx.obj.id_token = config.id_token

    ctx.obj.rm_socket_server = config.rm_socket_server
    ctx.obj.ml_image = config.ml_image
    ctx.obj.rm_config_volume = config.rm_config_volume
    ctx.obj.rm_manager_image = config.rm_manager_image
    ctx.obj.rm_container_name = config.rm_container_name

    return ctx
