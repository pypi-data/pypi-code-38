from argus_cli.plugin import create_module, import_external_plugins
from argus_plugins.api_provider import argus_api

__all__ = [
    "assets",
    "cases",
    "customer_networks",
    "datastore",
    "documents",
    "events",
    "reports",
    "generate",
]

# Initialize the toolbelt with the framework.
argus_cli_module = create_module(providers=[argus_api])

# FIXME: Dirty hack because argus_api is generated during runtime.
#        If this isn't done, the imports are not done in the correct order.
#        Can be fixed by bundling a generated version of the api (which we honestly should do).
#
#        Now the API has to be loaded like this, even though we have the provider.
argus_api()

# TODO: Improve this implementation. Should have a clearer API.
import_external_plugins("argus_cli.plugins")
