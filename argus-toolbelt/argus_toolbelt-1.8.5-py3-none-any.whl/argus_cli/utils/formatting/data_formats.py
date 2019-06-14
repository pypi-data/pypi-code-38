from collections import defaultdict

NOT_AVAILABLE_TEXT = ""


class _defaultdict(defaultdict):
    """This class is introduced because by default default dicts will print as a class, not a dict."""

    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return str(dict(self))


def _dict_to_default_dict(d: dict) -> dict:
    """Converts a dict to a default dict.

    This is done to convert dicts to

    :param d: A dictionary with data
    :return: A dictionary that will return "not available" when accessing non-existing indices.
    """
    if isinstance(d, dict):
        for key, value in d.items():
            d[key] = _dict_to_default_dict(value)
        d = _defaultdict(lambda: NOT_AVAILABLE_TEXT, **d)
    return d


def formatted(
        data: list, formatter: callable,
        headers: list = None, show_headers: bool = True
) -> str:
    """Helper for creating formatted outputs

    :param data: Data to output
    :param formatter: Function that turns a list of data into a string based on the headers
    :param headers: Headers of the data, defaults to the keys of the first piece of data.
    :param show_headers: Whether or not to display the headers
    :returns: A formatted string based on the input-data
    """
    if not headers:
        try:
            headers = data[0].keys()
        except IndexError:
            # If there is no data
            headers = []

    out = []

    if show_headers:
        out.append(formatter(
            {header: header for header in headers},
            headers,
            is_header=True
        ))

    for row in data:
        row = _dict_to_default_dict(row)
        out.append(formatter(row, headers))

    return "\n".join(out)


def _flatten_data(row: dict, headers: list):
    """Flatten the data and put it in the same order as the headers."""
    if isinstance(row, dict):
        return [str(row[field]) for field in headers]
    else:
        # Assumes that if it isn't dict, it's a class with attrs
        return [str(getattr(row, field)) for field in headers],


def jira_table(data: list, **kwargs):
    """Outputs a JIRA table

    :param data: A list of dicts to format.
    :param kwargs: Parameters passed to `formatted`.
    """
    def table_formatter(row: dict, headers: list, is_header=False, **kwargs):
        seperator = "||" if is_header else "|"
        return seperator + seperator.join(_flatten_data(row, headers)) + seperator

    return formatted(data, table_formatter, **kwargs)


def csv(data: list, **kwargs):
    """Standard CSV printer

    :param data: A list of dicts to format.
    :param kwargs: Parameters passed to `formatted`.
    """
    def csv_formatter(row: dict, headers: list, **kwargs):
        return ",".join(_flatten_data(row, headers))

    return formatted(data, csv_formatter, **kwargs)


def formatted_string(data: list, format_string: str, **kwargs) -> str:
    """Using format-strings for outputs.

    Simply calls .format(...) on the supplied string

    :param data: A list of dicts to format.
    :param format_string: The string to use when outputting.
    :param kwargs: Parameters passed to `formatted`.
    """
    if "show_headers" not in kwargs:
        kwargs["show_headers"] = False

    def string_formatter(row: dict, headers: list, **kwargs):
        return format_string.format(**row)

    return formatted(data, string_formatter, **kwargs)
