import logging
import sys
from argparse import ArgumentParser, RawTextHelpFormatter

import toml

from fran import __version__
from fran.common import parse_keys, setup_logging
from fran.gui import run
from fran.constants import (
    CONTROLS,
    DEFAULT_FPS,
    DEFAULT_CACHE_SIZE,
    DEFAULT_THREADS,
    DEFAULT_FLIPX,
    DEFAULT_FLIPY,
    DEFAULT_ROTATE,
    DEFAULT_KEYS,
    default_config,
)


logger = logging.getLogger(__name__)


def parse_args():
    parser = ArgumentParser(
        description="Log video (multipage TIFF) frames in which an event starts or ends",
        epilog=CONTROLS,
        prog="fran",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--write_config",
        "-w",
        help="Write back the complete config to a file at this path, then exit",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        help="Path to CSV for loading/saving. "
        "If no path is selected when you save, a file dialog will open.",
    )
    parser.add_argument("--config", "-c", help="Path to TOML file for config")
    parser.add_argument(
        "--fps",
        "-f",
        type=float,
        default=DEFAULT_FPS,
        help=f"Maximum frames per second; default {DEFAULT_FPS}",
    )
    parser.add_argument(
        "--cache",
        "-n",
        type=int,
        default=DEFAULT_CACHE_SIZE,
        help=f"Number of frames to cache (increase if reading over a network and you have lots of RAM); default {DEFAULT_CACHE_SIZE}",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=DEFAULT_THREADS,
        help=f"number of threads to use for reading file (increase if reading over a network); default {DEFAULT_THREADS}",
    )
    parser.add_argument(
        "--keys",
        "-k",
        type=parse_keys,
        default=dict(),
        help='Optional mappings from event name to key, in the format "w=forward,a=left,s=back,d=right". '
        "These are additive with those defined in the config",
    )
    parser.add_argument(
        "--flipx",
        "-x",
        action="store_true",
        default=DEFAULT_FLIPX,
        help="Flip image in x",
    )
    parser.add_argument(
        "--flipy",
        "-y",
        action="store_true",
        default=DEFAULT_FLIPY,
        help="Flip image in y",
    )
    parser.add_argument(
        "--rotate",
        "-r",
        type=float,
        default=DEFAULT_ROTATE,
        help="Rotate image (degrees counterclockwise; applied after flipping)",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version and then exit"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Increase verbosity of logging (can be repeated). One for DEBUG, two for FRAME.",
    )
    parser.add_argument("--logfile", "-l", help="File to save log to")
    parser.add_argument(
        "infile",
        nargs="?",
        default=None,
        help="Path to multipage TIFF file to read. If no path is given, a file dialog will open.",
    )

    parsed = parser.parse_args()

    setup_logging(parsed.verbose, parsed.logfile)

    if parsed.version:
        print(__version__)
        sys.exit(0)

    keys_mapping = DEFAULT_KEYS.copy()

    if parsed.config:
        logger.info("Loading config file from %s", parsed.config)
        config = toml.load(parsed.config)

        for setting_key in ("fps", "cache", "threads"):
            if getattr(parsed, setting_key) is None:
                setattr(
                    parsed,
                    setting_key,
                    config.get("settings", dict()).get(
                        setting_key, default_config["settings"][setting_key]
                    ),
                )

        keys_mapping.update(config.get("keys", dict()))

    keys_mapping.update(parsed.keys)
    parsed.keys = keys_mapping

    if parsed.write_config:
        logger.info("Writing config file to %s and exiting", parsed.write_config)
        d = {
            "settings": {
                "fps": parsed.fps,
                "cache": parsed.cache,
                "threads": parsed.threads,
            },
            "transform": {
                "flipx": parsed.flipx,
                "flipy": parsed.flipy,
                "rotate": parsed.rotate,
            },
            "keys": parsed.keys,
        }
        with open(parsed.write_config, "w") as f:
            toml.dump(d, f)
        sys.exit(0)

    return parsed


def main():
    parsed_args = parse_args()
    return run(
        parsed_args.infile,
        parsed_args.outfile,
        parsed_args.cache,
        parsed_args.fps,
        parsed_args.threads,
        parsed_args.keys,
        parsed_args.flipx,
        parsed_args.flipy,
        parsed_args.rotate,
    )


if __name__ == "__main__":
    sys.exit(main())
