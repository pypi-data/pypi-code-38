from collections import defaultdict

from argus_api.api.events.v1.aggregated import find_aggregated_events
from argus_cli.plugin import register_command
from argus_cli.helpers.log import log
from argus_cli.utils.arguments import organize_parameters
from argus_cli.utils.formatting import get_data_formatter
from argus_cli.utils.time import timestamp_to_date, date_or_relative
from argus_plugins import argus_cli_module

from argus_plugins.cases.utils import get_customer_id
from argus_plugins.events import utils


argument_api_name_map = {
    "customer": "customerID",
    "flag": "includeFlags",
    "alarm": "alarmID",
    "ip": "ip",
    "source_ip": "sourceIP",
    "destination_ip": "destinationIP",
    "signature": "signature",
    "properties": "properties"
}


def rename_variables(parameters: dict) -> tuple:
    """Renames input parameters to a more programmable format

    :param parameters: Parameters to convert
    :return: Include and exclude parameters in dicts
    """
    include = {
        argument_api_name_map[key.replace("include_", "")]: value
        for key, value in parameters.items()
        if key.startswith("include_") and value
    }
    exclude = {
        argument_api_name_map[key.replace("exclude_", "")]: value
        for key, value in parameters.items()
        if key.startswith("exclude_") and value
    }

    if "includeFlags" in exclude.keys():
        # Hack because include/exclude flag differs from all other parameters
        include["excludeFlags"] = exclude.pop("includeFlags")

    return include, exclude


def format_event(event: dict) -> dict:
    """Replaces some keys from the event to human readable format

    The following keys are modified:
        r"*timestamp*": Timestamp to ISO8601 date-time format.

    :param event: Event to modify
    :returns: Modified event
    """
    for time_key in filter(lambda key: "timestamp" in key.lower(), event.keys()):
        event[time_key] = timestamp_to_date(event[time_key] / 1000)

    return event


@register_command(extending="events", module=argus_cli_module)
def search(start: date_or_relative, end: date_or_relative,
           format: get_data_formatter = "csv",
           include_customer: get_customer_id = None, exclude_customer: get_customer_id = None,
           include_flag: utils.FLAGS = None, exclude_flag: utils.FLAGS = None,
           include_alarm: int = None, exclude_alarm: int = None,
           include_ip: str = None, exclude_ip: str = None,
           include_source_ip: str = None, exclude_source_ip: str = None,
           include_destination_ip: str = None, exclude_destination_ip: str = None,
           include_signature: str = None, exclude_signature: str = None,
           include_properties: dict = None, exclude_properties: dict = None,
           min_severity: utils.SEVERITIES = "high"):
    """Searches for events in argus.

    Include and exclude parameters are mimics the aggregated event search endpoint,
    and can be found in the api documentation.

    Example use:
        argus-cli events search "2 days ago" "now"
            --format json
            --include-properties '{"argus.timestamp": 9001, "uhost": "host.example.com"}'

    :param start: Start time of the search in ISO8016 format (Example: 2018-01-01)
    :param end: End time of the search in ISO8016 format (Example: 2018-01-01)
    :param format: Follows the normal str.format() syntax.
    :param list include_customer: Customer(s) to include
    :param list exclude_customer: Customer(s) to exclude
    :param list include_flag: Flag(s) to include
    :param list exclude_flag: Flag(s) to exclude
    :param list include_alarm: Alarm ID(s) to include
    :param list exclude_alarm: Alarm ID(s) to exclude
    :param list include_ip: IP(s) to include
    :param list exclude_ip: IP(s) to exclude
    :param list include_source_ip: Source IP(s) to include
    :param list exclude_source_ip: Source IP(s) to exclude
    :param list include_destination_ip: Destination IP(s) to include
    :param list exclude_destination_ip: Destination IP(s) to exclude
    :param list include_signature: Signature(s) to include
    :param list exclude_signature: Signature(s) to exclude
    :param include_properties: Properties to include
    :param exclude_properties: Properties to exclude
    :param min_severity: Minimum severity of events

    :alias format: format-string
    """
    log.info("Organizing parameters...")
    include, exclude = rename_variables(locals())
    parameters = organize_parameters(include, exclude)

    log.info("Getting events from Argus...")
    events = find_aggregated_events(
        limit=10000,
        startTimestamp=start, endTimestamp=end,
        minSeverity=min_severity,
        **parameters
    )["data"]

    if not events:
        log.info("There are no events in the search.")
        return

    log.info("Formatting output to human-readable format...")
    for event in events:
        event = format_event(event)

    log.info("Printing output...")
    print(format(events))
