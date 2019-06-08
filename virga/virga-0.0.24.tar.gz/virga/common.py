from importlib import import_module


class VirgaException(Exception):
    """Custom exception for Virga."""


def get_provider_class(args: any) -> any:
    """
    Return an instance of the Provider based on the name in the configuration.

    :param args: Command line args
    :return: An instance of the Provider
    """
    try:
        provider_module = import_module('virga.providers.%s' % args.provider)
        return provider_module.Provider(args)
    except ModuleNotFoundError:
        raise VirgaException('Provider module not found')
    except AttributeError:
        raise VirgaException('Provider class not found')
