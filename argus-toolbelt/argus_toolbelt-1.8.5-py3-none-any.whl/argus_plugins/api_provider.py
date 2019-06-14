from api_generator import load
from argus_cli import register_provider
from argus_cli.settings import settings


# TODO: Debug isn't used, but rather look at settings._get_debug_mode.
#       This should be fixed.
# TODO: Environment isn't used, same thing as with --debug.
@register_provider()
def argus_api(apikey: str = None, debug: bool = False, environment: str = None) -> None:
    """Argus CLI provider"""
    if apikey:
        settings["api"]["api_key"] = apikey

    load(settings["api"]["api_url"], settings["api"]["definitions"])
