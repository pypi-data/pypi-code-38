from datetime import datetime

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_cli.utils import time
from argus_api.api.cases.v2.case import advanced_case_search
from argus_plugins import argus_cli_module

from argus_plugins.cases import utils

GROUPINGS = {
    "year": lambda case: datetime.fromtimestamp(case["createdTimestamp"] / 1000).strftime("%Y"),
    "month": lambda case: datetime.fromtimestamp(case["createdTimestamp"] / 1000).strftime("%Y-%m"),
    "week": lambda case: datetime.fromtimestamp(case["createdTimestamp"] / 1000).strftime("%Y-W%W"),
    "user": lambda case: case["createdByUser"]["userName"] if "createdByUser" in case else "N/A",
}


def group_cases(cases: list, group_by: str) -> dict:
    groups = {}
    grouping = GROUPINGS[group_by]

    for case in cases:
        group = grouping(case)
        if group not in groups:
            groups[group] = []
        groups[group].append(case)

    return groups


def sort_cases(cases: list) -> dict:
    """Sorts cases based on their priority"""
    sorted = {priority: [] for priority in utils.PRIORITIES}
    for case in cases:
        sorted[case["priority"]].append(case)

    return sorted


def print_statistics(cases: dict, grouping: str):
    """Prints the statistics as a CSV"""
    headers = [grouping]
    headers.extend(utils.PRIORITIES)
    print(",".join(headers))

    for group_id, group in sorted(cases.items()):
        stats = [str(len(group[priority])) for priority in utils.PRIORITIES]
        print("{group},{stats}".format(group=group_id, stats=",".join(stats)))


@register_command(extending="cases", module=argus_cli_module)
def statistics(
        start: time.date_or_relative, end: time.date_or_relative,
        customer: utils.get_customer_id = None,
        group_by: GROUPINGS = "week",
        case_type: utils.CASE_TYPES = None,
        category: str = None,
        service: str = None,
        status: utils.STATUSES = None
):
    """Shows the statistics about how many cases there are of each severity.

    :param start: The time of the first case
    :param end: The time of the last case
    :param list customer: The customer to search for
    :param group_by: How the info will be grouped
    :param list case_type: Type to search for
    :param list category: The category to search for
    :param list service: The service to search for
    :param list status: Status to search for
    :return:
    """
    log.info("Getting cases...")
    cases = advanced_case_search(
        limit=0,
        startTimestamp=start, endTimestamp=end, timeFieldStrategy=["createdTimestamp"],
        customerID=customer,
        type=case_type, category=category, service=service,
        status=status
    )["data"]

    log.info("Grouping cases...")
    cases = group_cases(cases, group_by)

    log.info("Sorting cases...")
    for group_id, group in cases.items():
        cases[group_id] = sort_cases(group)

    log.info("Printing statistics...")
    print_statistics(cases, group_by)
