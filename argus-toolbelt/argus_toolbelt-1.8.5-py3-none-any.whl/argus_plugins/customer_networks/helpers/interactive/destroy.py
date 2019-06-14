from datetime import datetime

from argus_api.api.customernetworks.v1.network import delete_customer_network
from api_generator.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.formatting import success, failure
from argus_cli.helpers.log import log
from argus_plugins.customer_networks.helpers.diff import diff_table


def destroy(
        networks: list,
        customer: dict,
        as_json: bool = False,
        dry: bool = False,
        skip_confirmation: bool = False
    ) -> list:
    """Destroys existing networks

    :param list networks: List of CustomerNetworks
    :param dict customer: Customer object (used only for logging)
    :param bool as_json: Messages are returned as JSON
    :param callable authenticate: Authentication method to pass in authentication headers to API functions
    :param bool interactive: Whether or not to ask the user for each network. Defaults to asking once only.
    :returns: List of messages for summary report
    """
    # Print updates and let user accept before performing updates
    summary = []

    for index, network in enumerate(networks):
        # Clear terminal when interactive:
        formatting.clear()

        # Print table of networks that will be destroyed
        print(
            formatting.table(
                data=[network],
                keys=("IP", "Description", "Zone", "Location", "Flags"),
                title='Remove network %s (%d of %d)' % (
                    network.to_json()['networkAddress'],
                    index + 1,
                    len(networks)
                ),
                format=formatting.red
            )
        )

        # Ask user to confirm the change unless we're running with alwaysYes
        if skip_confirmation or formatting.ask("Remove this network?"):
            log.info("Removing network for %s" % customer["name"])

            try:
                # Only perform the API action if we're not running in 
                # dry mode, in which case no actual changes will be made
                if not dry:
                    delete_customer_network(id=network['id'])
                
                # Add a success message to the summary report
                # Add success message to summary report
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Removed %s" % (network.to_json()["networkAddress"]),
                        "name": network["description"],
                        "ip": network.to_json()["networkAddress"],
                        "body": network.to_json(),
                        "updated": False,
                        "created": False,
                        "failure": False,
                        "deleted": True,
                    })
                else:
                    summary.append(
                        success(
                            "Network %s removed from Argus" % (
                                network.to_json()['networkAddress']
                            )
                        )
                    )
                    log.info(summary[-1])

            # Catch any HTTP errors and add the error messages to the 
            # summary report instead of crashing
            except ArgusException as error:
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Failed to remove network %s from Argus: %s" % (
                            network.to_json()['networkAddress'],
                            error
                        ),
                        "name": network["description"],
                        "ip": network.to_json()["networkAddress"],
                        "body": network.to_json(),
                        "updated": False,
                        "created": False,
                        "failure": False,
                        "deleted": True,
                    })
                else:
                    summary.append(
                        failure(
                            "Failed to remove network %s from Argus: %s" % (network.to_json()['networkAddress'], error)
                        )
                    )
                    log.error(summary[-1])
    return summary