"""Provides the wrapper class for Argus API"""
import site
import ssl
from distutils.sysconfig import get_python_lib
from os import getenv, makedirs
from os.path import exists, join

from datetime import datetime
from requests.exceptions import SSLError, Timeout, ProxyError
from types import ModuleType
from urllib3.exceptions import MaxRetryError

from api_generator.helpers.generator import write_endpoints_to_disk
from api_generator.helpers.log import log
from api_generator.helpers.module_loader import import_submodules
from api_generator.parsers import recursive_parser

API_DIRECTORY = site.USER_SITE if site.ENABLE_USER_SITE else get_python_lib()
API_OUTPUT_DIRECTORY = join(API_DIRECTORY, "argus_api", "api")


def _load_endpoints(parser: ModuleType, schema_uri: str):
    try:
        endpoints = parser.load(schema_uri)
    except (SSLError, Timeout, ProxyError, MaxRetryError, ssl.SSLError) as error:
        log.error(error)
        log.error("Please check that REQUESTS_CA_BUNDLE is set to the correct certificate if you're behind an SSL terminating proxy.")
        log.error("REQUESTS_CA_BUNDLE=%s" % getenv('REQUESTS_CA_BUNDLE'))
        exit(1)

    return endpoints


def generate_api_module(base_uri: str, location: str, parser: ModuleType = recursive_parser):
    """Regenerates the API into the default location

    :param base_uri: Base of the URI (eg. domain)
    :param location: Location of the swagger file
    :param parser: Parser to parse the definitions with
    """
    log.debug("Generating API module using %s%s..." % (base_uri, location))
    endpoints = _load_endpoints(parser, "%s%s" % (base_uri, location))

    if not exists(API_OUTPUT_DIRECTORY):
        log.debug("Creating module directory...")
        makedirs(API_OUTPUT_DIRECTORY)

    log.debug("Writing API modules to disk...")
    write_endpoints_to_disk(
        endpoints=endpoints,
        output=API_OUTPUT_DIRECTORY,
        api_url=base_uri,
        with_plugin_decorators=True
    )


def load(api_url: str, swagger_files: list, parser: ModuleType = recursive_parser) -> ModuleType:
    """Initializes, so that when called, the static API files will
    be generated to disk if they dont already exist, and the module then returned
    to the user. If the api module already exists, return the loaded module.

    :param api_url:
    :param swagger_files: Swagger files to load from the given api UPL
    :param parser: Optional custom parser module for parsing the schema before writing to disk
    """
    try:
        import argus_api.api

        # If the time of generation is older than 2 days, force regeneration
        time_ago = (datetime.now() - datetime.fromtimestamp(argus_api.api.__CREATED_AT__))
        if not hasattr(argus_api.api, "__API_URL__") or argus_api.api.__API_URL__ != api_url:
            log.info(
                "Argus API files have a different url than what was provided (%s). Re-generating..." % api_url
            )
            raise ImportError
        elif time_ago.days > 1:
            log.info("Argus API files are %d days old. Re-generating..." % time_ago.days)
            raise ImportError

    except ImportError:
        log.info("No static API files found. Generating them...")
        for schema in swagger_files:
            generate_api_module(api_url, schema, parser)

    # DONT swallow other exceptions!
    except Exception as error:
        log.error(error)
        exit(1)

    import argus_api.api
    import_submodules("argus_api.api", exclude_name="test_")
    return argus_api.api
