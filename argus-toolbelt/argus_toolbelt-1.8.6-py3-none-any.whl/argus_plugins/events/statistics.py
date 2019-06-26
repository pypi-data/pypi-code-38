from argus_api.api.events.v1.aggregated import find_aggregated_event_stats

from argus_cli.plugin import register_command
from argus_cli.helpers.log import log
from argus_cli.utils import time, formatting
from argus_cli.utils.formatting import get_data_formatter
from argus_plugins import argus_cli_module

from argus_plugins.events import utils
from argus_plugins.cases.utils import get_customer_id


def setup_fields(keys: list):
    headers = ["time", "count"]

    # Add the keys sent by Argus to the headers
    headers.extend([key for key in keys[0].keys() if key != "id"])

    return headers, keys


def create_presentable_data(time_frames: list, keys: list) -> list:
    """Creates presentable data from the returned statistics"""
    results = []

    for time_frame in time_frames:
        for record in time_frame["records"]:
            # Add constant data
            result = {
                "time": time.timestamp_to_date(time_frame["timeFrame"]["startTime"] / 1000),
                "count": record["value"]["count"],
            }

            # Add variable data
            for key, value in keys[record["keyID"] - 1].items():
                if key == "id":
                    # We don't want the ID field in our data
                    continue
                result[key] = value

            results.append(result)

    return results


@register_command(extending="events", module=argus_cli_module)
def statistics(
        start: time.date_or_relative, end: time.date_or_relative,
        customer: get_customer_id, resolution: time.time_diff = 0,
        group_by: utils.GROUPINGS = None, attack_category: int = None,
        count_raw_events: bool = False,
        format: get_data_formatter = "csv"
    ):
    """Prints statistical data about events with some specified criteria

    :param start: Start time of the search
    :param end: End time of the search
    :param list customer: Customers to search for
    :param resolution: The timeframe of results
    :param list group_by: Parameters to group by
    :param list attack_category: Attack category to display
    :param count_raw_events: Count the raw number of events instead of aggregated events
    :param format: How to format the output. Can be either jira-table, csv or a formatted string.
    """
    log.info("Getting events from argus...")
    data = find_aggregated_event_stats(
        startTimestamp=start, endTimestamp=end, customerID=customer, resolution=resolution,
        countRawEvents=count_raw_events, attackCategoryID=attack_category, groupBy=group_by,
    )["data"]

    headers, keys = setup_fields(data["keys"])

    log.info("Creating presentable data...")
    presentable_data = create_presentable_data(data["timeFrames"], keys)

    log.info("Printing statistics...")
    print(format(presentable_data, headers=headers))

