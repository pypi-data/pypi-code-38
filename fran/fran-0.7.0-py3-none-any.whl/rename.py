from argparse import ArgumentParser
import sys

import pandas as pd
import toml

from . import __version__
from .common import parse_keys, setup_logging, load_results, dump_results, df_to_str


def parse_args():
    parser = ArgumentParser(
        prog="fran-rename",
        description="Rename all of the events in a given results file, "
        "with a key mapping specified in a config TOML and/or command line argument.",
    )
    parser.add_argument("--config", "-c", help="Path to TOML file for config")
    parser.add_argument(
        "--keys",
        "-k",
        type=parse_keys,
        default=dict(),
        help='Optional mappings from event name to key, in the format "w=forward,a=left,s=back,d=right". '
        "These are additive with those defined in the config",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version and then exit"
    )
    parser.add_argument(
        "--print",
        "-p",
        action="store_true",
        help="Print results to stdout, instead of saving file back",
    )
    parser.add_argument("results", help="Path to CSV to update.")

    parsed = parser.parse_args()

    if parsed.version:
        print(__version__)
        sys.exit(0)

    keys_mapping = dict()
    if parsed.config:
        config = toml.load(parsed.config)
        keys_mapping.update(config.get("keys", dict()))

    keys_mapping.update(parsed.keys)
    parsed.keys = keys_mapping

    return parsed


def remap_df(df: pd.DataFrame, keys_mapping):
    df = df.copy()
    if keys_mapping:
        new_events = []
        for row in df.itertuples():
            new_events.append(keys_mapping.get(row.key, row.event) or row.key)

        df["event"] = new_events
    return df


def run(fpath, keys_mapping, dry_run=False):
    old = load_results(fpath)

    new = remap_df(old, keys_mapping)

    if dry_run:
        print(df_to_str(new))
    else:
        dump_results(new, fpath)


def main():
    setup_logging()
    parsed = parse_args()
    run(parsed.results, parsed.keys, parsed.print)


if __name__ == "__main__":
    main()
