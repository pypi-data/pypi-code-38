import pkg_resources


def riptide_engine_docker_assets_dir():
    return pkg_resources.resource_filename(__name__, 'assets')
