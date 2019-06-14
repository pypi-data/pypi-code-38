"""
GENERATOR PLUGIN
=====================

Generator is used to generate files based on templates — first and foremost, static API files. Generator creates the plugin hooks and redirects
to the appropriate generator methods, and can be run with:

argus-cli generate endpoint --name ENDPOINT_NAME -O api/folder/path
argus-cli generate endpoint --matching REGEX -O api/folder/path
argus-cli generate all

TODO: 
- Accept custom swagger.json URL
- Parse OAuth 3.0
- Resolve recursive references in JSONSchema
- Support different authentication modes from command line and generate authentication differently
- Templates for other languages
- Update API url from settings
"""
from os import mkdir, getcwd
from os.path import exists, join

from api_generator.helpers.generator import write_endpoints_to_disk
from api_generator import generate_api_module
from api_generator.parsers.recursive_parser import load
from argus_cli.settings import settings
from argus_cli.plugin import register_command, run
from api_generator import API_DIRECTORY

from argus_plugins import argus_cli_module


@register_command(module=argus_cli_module)
def all_endpoints(directory: str = '', as_plugins: bool = False) -> list:
    """Generates all endpoints to a given directory
    
    :param directory: Output directory
    :param as_plugins: Should API methods be written as argus toolbelt plugins?
    """
    
    for schema in settings["api"]["definitions"]:
        path = join(getcwd(), directory or API_DIRECTORY)
        if not directory:
            generate_api_module(settings["api"]["api_url"], schema)
        else:
            schema_location = "%s%s" % (settings["api"]["api_url"], schema)

            if not exists(path):
                mkdir(path)

            write_endpoints_to_disk(
                endpoints=load(schema_location),
                output=path,
                api_url=settings["api"]["api_url"],
                with_plugin_decorators=directory == API_DIRECTORY
            )


if __name__ == "__main__":
    run(all_endpoints)
