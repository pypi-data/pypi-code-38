from argus_cli.plugin import register_command
from argus_cli.utils.time import date_time_to_timestamp
from argus_cli.utils.formatting import formatted_string
from argus_api.api.reports.v1.search import simplified_search_reports
from argus_plugins import argus_cli_module

from argus_plugins.cases.utils import get_customer_id
from argus_plugins.reports import PERIOD


def _sort_reports(reports: list) -> tuple:
    """Sorts the reports into published and not published"""
    published = []
    not_published = []

    for report in reports:
        if report["status"] == "COMPLETED":
            published.append(report)
        else:
            not_published.append(report)

    return published, not_published


def _print_results(published: list, not_published: list, format_string: str) -> None:
    """Prints the results in two lists"""
    output = \
        "Not Published\n-------------\n" + \
        "{not_published}\n" + \
        "\n" + \
        "Published\n-------------\n" + \
        "{published}"

    output = output.format(
        not_published=formatted_string(not_published, format_string),
        published=formatted_string(published, format_string)
    )

    print(output)


@register_command("status", "reports", module=argus_cli_module)
def report_status(
        period: PERIOD,
        customer: get_customer_id = None,
        start: date_time_to_timestamp = None,
        end: date_time_to_timestamp = None,
        format_string: str = "{customer[name]} ({customer[shortName]}) - {description}"
):
    """Show what reports have been published and not published

    :param period: The period to view
    :param list customer: A set of customers to include in the search
    :param start: The start of the period (if in custom mode)
    :param end: The end of the period (if in custom mode)
    :param format_string: How each customer will be displayed (Used like str.format)
    """
    if period == "custom" and (not start or not end):
        print("A period has to be defined when having a custom period")
        exit(1)

    reports = simplified_search_reports(
        limit=0,
        startTime=start, endTime=end,
        period=period.upper(),
        customerID=customer
    )["data"]

    published, not_published = _sort_reports(reports)
    _print_results(published, not_published, format_string)
