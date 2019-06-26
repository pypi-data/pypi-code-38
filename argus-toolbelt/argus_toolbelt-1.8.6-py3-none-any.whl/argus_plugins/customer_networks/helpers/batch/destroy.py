from datetime import datetime

from argus_api.api.customernetworks.v1.network import delete_customer_network
from api_generator.exceptions.http import ArgusException
from argus_cli.helpers import formatting
from argus_cli.helpers.formatting import success, failure
from argus_cli.helpers.log import log


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
    :param callable authenticate: Authentication method to pass in authentication headers to API functions
    :param bool interactive: Whether or not to ask the user for each network. Defaults to asking once only.
    :param bool as_json: Messages are returned as JSON
    :returns: List of messages for summary report
    """
    # Print updates and let user accept before performing updates
    summary = []

    # Print a table of the networks that will be destroyed:
    print(
        formatting.table(
            data=networks,
            keys=("address", "description"),
            title='Remove networks for %s' % customer['name'],
            format=formatting.red
        )
    )

    # Ask the user to confirm the change unless we're running with
    # skip_confirmation (alwaysYes option)
    if skip_confirmation or formatting.ask('Accept changes?'):
        log.info("Removing networks for %s" % customer["name"])

        for network in networks:
            log.info(
                "Removing network %s for %s" % (
                    network.to_json()['networkAddress'],
                    customer["name"]
                )
            )

            try:

                # Only perform the API action if we're not running in dry
                # mode, in which case no changes will be pushed to Argus
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
                        success("Network %s removed from Argus" % (
                            network.to_json()['networkAddress']
                        ))
                    )
                    log.info(summary[-1])

            # Catch any error messages from the API and add them to the summary
            # report instead of crashing
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
                        failure("Failed to remove network %s from Argus: %s" % (
                            network.to_json()['networkAddress'],
                            error
                        ))
                    )
                    log.error(summary[-1])

    return summary