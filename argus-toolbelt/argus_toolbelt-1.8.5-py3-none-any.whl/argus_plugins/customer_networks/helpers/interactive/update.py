import json
from datetime import datetime

from argus_api.api.customernetworks.v1.network import update_customer_network
from api_generator.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.formatting import success, failure

from argus_cli.helpers.log import log
from argus_plugins.customer_networks.helpers.diff import diff_table


def update(
        networks: list,
        customer: dict,
        as_json: bool = False,
        dry: bool = False,
        skip_confirmation: bool = False
    ) -> list:
    """Updates existing networks

    :param list networks: List of CustomerNetworks
    :param bool as_json: Messages are returned as JSON
    :param bool dry: Whether any actual changes should be performed or not
    :param bool interactive: Ask the user to continue on each network?
    :return list[str]: Summary of messages produced
    """

    # Find all networks that have changed in the given list:
    dirty_networks = [n for n in networks if n.is_dirty()]

    # This will hold our messages (failure, success, etc), which we display at the end
    summary = []

    # If we're running in interactive mode, then print a difference 
    # table for each network that will be changed, and ask the user
    # to confirm each individual change instead
    for index, network in enumerate(dirty_networks):
        # Clear terminal when interactive:
        formatting.clear()
        print(
            formatting.table(
                data=diff_table([network]),
                keys=("IP", "Description", "Zone", "Location", "Flags"),
                title='Changes to %s (%d of %d)' % (
                    network.to_json()['networkAddress'],
                    index + 1,
                    len(networks)
                ),
            )
        )

        # Ask the user to confirm the change unless this has 
        # been overridden by skip_confirmation
        if skip_confirmation or formatting.ask("Accept changes?"):
            log.info("Updating networks for %s" % customer["name"])

            try:
                # Only perform API actions when not in dry mode
                if not dry:
                    # Update the network with its dirty
                    # (modified) fields before creating JSON
                    # from it
                    network.update(network._dirty)
                    update_customer_network(
                      **{
                            key: value
                            for key, value in network.to_json().items()
                            
                            # Allowed fields for update:
                            if key in (
                                'networkID',
                                'location',
                                'description',
                                'flagsToEnable',
                                'flagsToDisable'
                            )
                        }
                    )
                # Add success message to summary report
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Network %s updated on Argus" % (network.to_json()['networkAddress']),
                        "name": network["description"],
                        "ip": network.to_json()["networkAddress"],
                        "body": network.to_json(),
                        "updated": True,
                        "created": False,
                        "failure": False,
                        "deleted": False,
                    })
                else:
                    summary.append(
                        success(
                            "Network %s updated on Argus" % (
                                network.to_json()['networkAddress']
                            )
                        )
                    )
                    log.info(summary[-1])
            except ArgusException as error:
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Failed to update network %s on Argus: %s" % (
                            network.to_json()['networkAddress'], error
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
                        "Failed to update network %s on Argus: %s" % (
                            network.to_json()['networkAddress'],
                            error
                        )
                    )
                    )
                    log.error(summary[-1])
    return summary