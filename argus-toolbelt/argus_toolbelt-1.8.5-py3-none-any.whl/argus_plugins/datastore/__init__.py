import sys

from argus_api.api.datastores.v1.descriptor import get_descriptor
from argus_api.api.datastores.v1.store.store import get_entries_from_store_simplified

from argus_cli.plugin import register_command
from argus_cli.utils.formatting import formatted_string
from argus_plugins import argus_cli_module

from argus_plugins.datastore import synchronize


@register_command(extending="datastores", module=argus_cli_module)
def dump(datastore, key: str = None, customer: str = None):
    """Displays a more human readable version of a datastore

    :param datastore: The datastore to display
    :param list key: Filter to specific keys
    :param list customer: Customer(s) to filter by
    """
    store_info = get_descriptor(datastore)["data"]
    data = get_entries_from_store_simplified(dataStore=datastore, key=key, customerID=customer)["data"]

    print(
        "--- Datastore Metadata ---\n"
        "Datastore: {datastore}\n"
        "Type: {type}\n"
        "Behaviour: {behaviour}\n"
        "Global: {is_global}\n"
        "Lifetime: {lifetime}\n".format(
            datastore=datastore,
            type=store_info["dataType"], behaviour=store_info["behaviourType"],
            is_global=store_info["globalData"], lifetime=store_info["lifeTime"]
        )
    )

    format_string = \
        "{customer[name]} - " if not store_info["globalData"] else "" \
        + "{key}" if store_info["dataType"] == "LIST" else "{key}: {value}"
    print(
        "----- Datastore Data -----\n"
        + formatted_string(data, format_string)
    )


@register_command(extending="datastores", module=argus_cli_module)
def min_count(datastore: str, minimum_count: int):
    """Checks the size of a datastore.

    This command is typically used for tests in Nagios.
    It will exit with a failed state if the minimum size is less than the minimum

    :param datastore: The datastore to check
    :param minimum_count: The minimum allowed objects in the store.
    """
    # The limit is 1 because we don't care about the objects, only the count.
    count = get_entries_from_store_simplified(datastore, limit=1)["count"]

    if count >= minimum_count:
        print("OK - Found %d entries in datastore %s" % (count, datastore))
        sys.exit(0)
    else:
        print("CRITICAL - Found %d entries in datastore %s (threshold=%s)" % (count, datastore, minimum_count))
        sys.exit(2)
