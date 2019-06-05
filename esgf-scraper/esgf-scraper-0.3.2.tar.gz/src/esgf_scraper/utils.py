import shutil
import time
import urllib.parse as urlparse
from contextlib import ContextDecorator

import pandas as pd

from esgf_scraper import conf


class BlockTimer(ContextDecorator):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start

    def elapsed(self):
        return time.time() - self.start


def print_items(items, cols="all", default_term_width=200, show_index=True):
    """
    Pretty prints a list of items to stdout

    Parameters
    ----------
    items: list of dicts
        The items to be printed
    cols: str or list of strs
        The columns to be included in the output
    default_term_width: int
        Fallback terminal width if none is set

    """
    cols = cols.split(",") if isinstance(cols, str) else cols
    excluded_cols = [
        "_timestamp",
        "_version_",
        "access",
        "activity_drs",
        "citation_url",
        "data_specs_version",
        "dataset_id_template_",
        "further_info_url",
        "geo",
        "geo_units",
        "pid",
        "title",
        "variable",
        "url",
    ]
    # Strip out any length 1 arrays
    for item in items:
        for k, v in item.items():
            if isinstance(v, list) and len(v) == 1:
                item[k] = v[0]

    df = pd.DataFrame(items)
    if "_id" in df.columns:
        df = df.set_index("_id")
    for c in excluded_cols:
        if c in df:
            df.drop(c, axis=1, inplace=True)
    if cols != ["all"]:
        df = df[cols]
    terminal_size = shutil.get_terminal_size((default_term_width, 20))
    with pd.option_context(
        "display.max_rows",
        None,
        "display.max_columns",
        df.shape[1],
        "display.width",
        terminal_size.columns,
        "display.max_colwidth",
        default_term_width,
    ):
        print(df.to_string(index=show_index))


def parse_database_url(url):
    """Parses a database URL."""

    if url == "sqlite://:memory:":
        # this is a special case, because if we pass this URL into
        # urlparse, urlparse will choke trying to interpret "memory"
        # as a port number
        return {"engine": "sqlite", "name": ":memory:"}
        # note: no other settings are required for sqlite

    # otherwise parse the url as normal
    config = {}

    url = urlparse.urlparse(url)

    # Split query strings from path.
    path = url.path[1:]

    # If we are using sqlite and we have no path, then assume we
    # want an in-memory database (this is the behaviour of sqlalchemy)
    if url.scheme == "sqlite" and path == "":
        return {"engine": "sqlite", "name": ":memory:"}

    # Handle postgres percent-encoded paths.
    hostname = url.hostname or ""

    # Update with environment configuration.
    config.update(
        {
            "engine": url.scheme,
            "name": urlparse.unquote(path or ""),
            "user": urlparse.unquote(url.username or ""),
            "password": urlparse.unquote(url.password or ""),
            "host": hostname,
            "port": url.port or "",
        }
    )

    if ":" in path:
        config["name"] = path.split(":")[0]
        config["table"] = path.split(":")[1]

    return config


def get_database_info(table_name=None):
    db_name = parse_database_url(conf["database_url"])

    if db_name["engine"] != "sqlite":
        raise ValueError("Only sqlite databases are currently supported")

    if table_name is not None:
        pass
    return db_name
