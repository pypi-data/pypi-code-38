import json
from datetime import datetime

from argus_api.api.customernetworks.v1.network import add_customer_network
from api_generator.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.formatting import success, failure

from argus_cli.helpers.log import log
from argus_plugins.customer_networks.helpers.diff import diff_table


def create(
        networks: list,
        customer: dict,
        dry: bool = False,
        as_json: bool = False,
        skip_confirmation: bool = False
    ) -> list:
    """Creates networks on Argus from a given list of CustomerNetworks

    :param list networks: List of CustomerNetworks
    :param bool as_json: Messages are returned as JSON
    :returns: Summary report as a list of messages
    """

    # Print updates and let user accept before performing updates
    summary = []

    # If we have networks to create, and we're not running in interactive mode,
    # perform the action on all networks without asking the user for each
    # network. Only ask once, after showing the difference.

    # Print the difference table showing which networks will be
    # updated and with what new values they will be updated
    print(
        formatting.table(
          title='New networks for %s' % customer['name'],
          keys=("IP", "Description", "Zone", "Location", "Flags"),
          data=diff_table(networks, show_only_changes=True),
        )
    )

    # Ask the user to confirm the change if we're not running with 
    # `skip_confirmation`
    if skip_confirmation or formatting.ask('Accept changes?'):
        log.info("Creating networks for %s" % customer["name"])

        for network in networks:
            log.info(
                "Creating network %s for %s" % (
                    network.to_json()['networkAddress'],
                    customer["name"]
                )
            )

            try:
                # Only perform API actions when we're not running
                # in dry mode
                if not dry:
                    # json.dumps can't dump dict_items, so we force it to a dict first
                    # and filter out flagsToDisable
                    log.debug(
                    json.dumps({
                        field: value
                        for field, value in network.to_json().items()
                        if field not in ('flagsToDisable', 'flagsToEnable')
                    })
                    )

                    add_customer_network(
                    **{
                        field: value
                        for field, value in network.to_json().items()
                        # These fields are prohibited for the create action, instead
                        # we can pass `flags`
                        if field not in ('flagsToDisable', 'flagsToEnable')
                    }
                    )

                # Add success message to summary report
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Created %s" % (network.to_json()["networkAddress"]),
                        "name": network["description"],
                        "ip": network.to_json()["networkAddress"],
                        "body": network.to_json(),
                        "updated": False,
                        "created": True,
                        "failure": False,
                        "deleted": False,
                    })
                else:
                    summary.append(
                        success(
                            "Network %s created on Argus" % (network.to_json()['networkAddress'])
                        )
                    )
                    log.info(summary[-1])

            # If we received a HTTP error, add the error message
            # to the summary report and log an error.
            except ArgusException as error:
                if as_json:
                    summary.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Failed to create network %s on Argus: %s" % (network.to_json()['networkAddress'], error),
                        "name": network["description"],
                        "ip": network.to_json()["networkAddress"],
                        "body": network.to_json(),
                        "updated": False,
                        "created": True,
                        "failure": False,
                        "deleted": False,
                    })
                else:
                    summary.append(
                        failure("Failed to create network %s on Argus: %s" % (
                            network.to_json()['networkAddress'], error
                        ))
                    )
                    log.error(summary[-1])

    return summary