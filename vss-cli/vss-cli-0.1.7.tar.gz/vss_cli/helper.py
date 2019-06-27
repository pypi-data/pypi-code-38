"""Helpers used by Home Assistant CLI (hass-cli)."""
import contextlib
from http.client import HTTPConnection
import json
import logging
import re
import shlex
from typing import Any, Dict, Generator, List, Optional, Tuple, cast

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer
from ruamel.yaml import YAML
from tabulate import tabulate
import vss_cli.const as const
import vss_cli.yaml as yaml

_LOGGING = logging.getLogger(__name__)


def to_attributes(entry: str) -> Dict[str, str]:
    """Convert list of key=value pairs to dictionary."""
    if not entry:
        return {}

    lexer = shlex.shlex(entry, posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ','
    attributes_dict = {}  # type: Dict[str, str]
    attributes_dict = dict(
        pair.split('=', 1) for pair in lexer  # type: ignore
    )
    return attributes_dict


def to_tuples(entry: str) -> List[Tuple[str, str]]:
    """Convert list of key=value pairs to list of tuples."""
    if not entry:
        return []

    lexer = shlex.shlex(entry, posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ','
    attributes_list = []  # type: List[Tuple[str,str]]
    attributes_list = list(
        tuple(pair.split('=', 1)) for pair in lexer  # type: ignore
    )
    return attributes_list


def raw_format_output(
    output: str,
    data: List[Dict[str, Any]],
    yamlparser: YAML,
    columns: Optional[List] = None,
    no_headers: bool = False,
    table_format: str = 'plain',
    sort_by: Optional[str] = None,
    single: Optional[str] = None,
    highlighted: bool = True,
) -> str:
    """Format the raw output."""
    if output == 'auto':
        _LOGGING.debug(
            "Output `auto` thus using %s",
            const.DEFAULT_DATA_OUTPUT
        )
        output = const.DEFAULT_DATA_OUTPUT

    if sort_by:
        _sort_table(data, sort_by)

    if output == 'json':
        try:
            if highlighted:
                return highlight(
                    json.dumps(data, indent=2,
                               sort_keys=False),
                    JsonLexer(),
                    TerminalFormatter()
                )
            else:
                return json.dumps(
                    data, indent=2,
                    sort_keys=False
                )
        except ValueError:
            return str(data)
    elif output == 'yaml':
        try:
            if highlighted:
                return highlight(
                    cast(
                        str,
                        yaml.dump_yaml(
                            yamlparser,
                            data
                        )
                    ),
                    YamlLexer(),
                    TerminalFormatter()
                )
            else:
                return cast(
                    str,
                    yaml.dump_yaml(
                        yamlparser,
                        data
                    )
                )
        except ValueError:
            return str(data)
    elif output == 'table':
        from jsonpath_rw import parse

        if not columns:
            columns = const.COLUMNS_DEFAULT

        fmt = [(v[0], parse(v[1] if len(v) > 1 else v[0])) for v in columns]
        result = []
        if single:
            dat = data[0]
            for fmtpair in fmt:
                val = [match.value for match in fmtpair[1].find(dat)]
                val_str = ", ".join(map(str, val))
                line = const.COLUMNS_TWO_FMT.format(fmtpair[0], val_str)
                result.append(line)
            res = '\n'.join(result)
            return res
        else:
            if no_headers:
                headers = []  # type: List[str]
            else:
                headers = [v[0] for v in fmt]
            for item in data:
                row = []
                for fmtpair in fmt:
                    val = [match.value for match in fmtpair[1].find(item)]
                    row.append(", ".join(map(str, val)))

                result.append(row)

            res = tabulate(
                result, headers=headers, tablefmt=table_format
            )  # type: str
            return res
    else:
        raise ValueError(
            f"Output Format was {output}, expected either 'json' or 'yaml'"
        )


def _sort_table(result: List[Any], sort_by: str) -> List[Any]:
    from jsonpath_rw import parse

    expr = parse(sort_by)

    def _internal_sort(row: Dict[Any, str]) -> Any:
        val = next(iter([match.value for match in expr.find(row)]), None)
        return (val is None, val)

    result.sort(key=_internal_sort)
    return result


def format_output(
    ctx,
    data: List[Dict[str, Any]],
    columns: Optional[List] = None,
    single: Optional[bool] = False
) -> str:
    """Format data to output based on settings in ctx/Context."""
    return raw_format_output(
        ctx.output,
        data,
        ctx.yaml(),
        columns,
        ctx.no_headers,
        ctx.table_format,
        ctx.sort_by,
        single=single
    )


def debug_requests_on() -> None:
    """Switch on logging of the requests module."""
    HTTPConnection.set_debuglevel(cast(HTTPConnection, HTTPConnection), 1)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def debug_requests_off() -> None:
    """Switch off logging of the requests module.

    Might have some side-effects.
    """
    HTTPConnection.set_debuglevel(cast(HTTPConnection, HTTPConnection), 1)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False


@contextlib.contextmanager
def debug_requests() -> Generator:
    """Yieldable way to turn on debugs for requests.

    with debug_requests(): <do things>
    """
    debug_requests_on()
    yield
    debug_requests_off()


def get_hostname_from_url(
        url: str,
        hostname_regex: str = const.DEFAULT_HOST_REGEX
) -> str:
    """Parse hostname from URL"""
    re_search = re.search(hostname_regex, url)
    _, _hostname = re_search.groups() if re_search else ('', '')
    _host = _hostname.split('.')[0] if _hostname.split('.') else ''
    return _host


def capitalize(
        value: str
) -> str:
    """Capitalize string"""
    return re.sub(
        r"(\w)([A-Z])", r"\1 \2",
        value
    ).title()


def str2bool(value: str) -> bool:
    return value.lower() in ("yes", "true", "t", "1", "y")


def dump_object(
        obj: Any, _key: str = None, _list: List[str] = None
) -> None:
    """Dumps dictionary in kv fmt"""
    for key, value in obj.items():
        if isinstance(value, list):
            for i in value:
                if isinstance(i, dict):
                    dump_object(i, key, _list)
                else:
                    _list.append(
                        const.COLUMNS_TWO_FMT.format(key, i)
                    )
        elif not isinstance(value, dict) and not isinstance(value, list):
            _k = _key + '.' + key
            _list.append(
                const.COLUMNS_TWO_FMT.format(
                    _k, value)
            )
        elif key not in ['_links']:
            dump_object(value, key, _list)
