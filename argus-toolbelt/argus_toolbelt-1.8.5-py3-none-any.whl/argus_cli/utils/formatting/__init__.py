"""Common formatting helpers for inputs and outputs to allow for a common interface across commands."""
import json
from functools import partial

from argus_cli.utils.formatting.data_formats import csv, jira_table, formatted_string

FORMATS = {
    "csv": csv,
    "json": partial(json.dumps, indent=2),
    "jira-table": jira_table,
}


def get_data_formatter(format: str) -> callable:
    """Convenience function to get a format

    If the given format isn't known, it will be interpreted as a formatted string.

    :param format: A format string or one of the available formats
    """
    try:
        return FORMATS[format]
    except KeyError:
        return partial(formatted_string, format_string=format)
