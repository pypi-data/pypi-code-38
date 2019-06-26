
import json
from argus_cli.plugin import register_command
from argus_cli.helpers import formatting
from api_generator.helpers import authentication

from argus_api.api.customers.v1.customer import get_customer_by_shortname
from argus_api.api.customernetworks.v1.network import search_customer_network
from argus_plugins import argus_cli_module

from .customer_network import CustomerNetwork
from .helpers import interactive as interactive_action, batch as batch, diff


@register_command(extending="customer-networks", module=argus_cli_module)
def update(
    customer: str,
    file: str,
    format: str = "address,description",
    first_line_defines_format: bool = False,
    always_yes: bool = False,
    replace: bool = False,
    interactive: bool = False,
    delete_missing: bool = False,
    splunk: bool = False,
    output: str = "",
    delimiter: str = ",",
    dry: bool = False,
) -> None:
    """
    Update customer networks from CSV file

    :param customer: Customer shortname
    :param file: Path to CSV file
    :param format: CSV format (available fields: address, description, subnetmask, zone)
    :param first_line_defines_format: If set, --format will be ignored and the CSV file is assumed to define the fields on the first line
    :param always_yes: Skip confirmation on updates (WARNING: If run with Replace, this will always replace existing networks, if run with Delete, networks not found in CSV will always be deleted from Argus! Use with caution.)
    :param replace: Update networks that already exist with new information
    :param delete_missing: Remove networks on Argus if they dont exist in the file (update, create from file and remove from argus)
    :param delimiter: CSV delimiter character
    :param interactive: Performs updates interactively and requires user to confirm each change
    :param dry: Performs a dry run - no updates will be sent to Argus
    :param splunk: Suppresses log and writes JSON output instead
    :param output: Used in conjunction with the splunk flag to write JSON to file
    :alias file: csv
    :alias format: F
    :alias first_line_defines_format: L
    :alias always_yes: y
    :alias replace: R
    :alias delete_missing: X
    :alias delimiter: t
    :alias interactive: i
    :alias dry: D

    """
    # Find customer by name
    customer = get_customer_by_shortname(shortName=customer)

    if not customer:
        raise LookupError(
            'No customer has been selected. Customer is required to edit customer networks.')

    customer = customer["data"]

    # Otherwise select the only customer
    # Fetch all networks for customer
    existing_networks = search_customer_network(
        customerID=[customer["id"]],
        # Setting limit to -1 does nothing, and 0 sets default limit to 25
        limit=0
    )

    # Convert them to CustomerNetwork objects
    existing_networks = list(
        map(CustomerNetwork.from_json, existing_networks["data"]))

    changes = diff.diff_file_vs_argus(
        network_list=CustomerNetwork.from_csv(
            file,
            header_format=None if first_line_defines_format else format.split(
                ','),
            headers_on_first_line=first_line_defines_format,
            delimiter=delimiter,
            customer=customer,
        ),
        existing_networks=existing_networks
    )

    messages = []

    if interactive:
        create = interactive_action.create
        update = interactive_action.update
        destroy = interactive_action.destroy
    else:
        create = batch.create
        update = batch.update
        destroy = batch.destroy

    if replace and len(changes['CHANGED_IN_FILE']):
        messages += update(
            changes['CHANGED_IN_FILE'],
            customer,
            dry=dry,
            as_json=splunk,
            skip_confirmation=always_yes
        )

    if len(changes['NOT_ON_SERVER']):
        messages += create(
            changes['NOT_ON_SERVER'],
            customer,
            dry=dry,
            as_json=splunk,
            skip_confirmation=always_yes
        )

    if delete_missing and len(changes['NOT_IN_FILE']):
        messages += destroy(
            changes['NOT_IN_FILE'],
            customer,
            dry=dry,
            as_json=splunk,
            skip_confirmation=always_yes
        )

    # Print summary
    if len(messages):
        if splunk:
            if output:
                with open(output, "w") as json_file:
                    json_file.write(json.dumps(messages))
            else:
                print(json.dumps(messages, indent=4))
        else:
            formatting.clear()
            print(
                formatting.table(
                    data=[{"message": msg} for msg in messages],
                    title="Summary",
                    keys=["message"]
                )
            )
    else:
        print("No action required.")
