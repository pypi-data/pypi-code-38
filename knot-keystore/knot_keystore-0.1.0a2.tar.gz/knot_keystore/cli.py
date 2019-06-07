# Copyright (c) 2019 Workonline Communications (Pty) Ltd. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""knot_keystore cli module."""

import argparse
import logging

import yaml

from knot_keystore.archive import get_plugins

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "/etc/knot-keystore.yaml"


def parse_args():
    """Parse command line args."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", "-s",
                        default="/run/knot/knot.sock",
                        help="path to knotc control socket")
    parser.add_argument("--plugins", "-p",
                        choices=get_plugins(),
                        nargs="*",
                        help="select archival plugins")
    parser.add_argument("--config-file", "-c",
                        default=DEFAULT_CONFIG_PATH,
                        help="path to a configuration file")
    parser.add_argument("-v", dest="verbosity",
                        default=0,
                        action="count",
                        help="increase output verbosity")
    args = parser.parse_args()
    return args


def set_loglevel(verbosity=0):
    """Set logging level."""
    level = 40 - (verbosity * 10)
    logging.basicConfig(level=level)
    return


def read_config(file=None):
    """Read configuration from a file."""
    log.debug(f"Trying to read config from {file}")
    try:
        with open(file) as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError as e:
        if file == DEFAULT_CONFIG_PATH:
            log.warning("Default config file not found")
            config_data = {"plugins": {}}
        else:
            log.error(f"Failed to open config file: {e}")
            raise e
    except Exception as e:
        log.error(f"Failed to load yaml from config file: {e}")
        raise e
    config = argparse.Namespace(**config_data)
    return config


def main():
    """Execute knot-keystore cli utility."""
    try:
        args = parse_args()
        set_loglevel(verbosity=args.verbosity)
        config = read_config(file=args.config_file)
        for plugin_name in config.plugins.keys():
            if args.plugins and plugin_name not in args.plugins:
                continue
            plugin_class = get_plugins(name=plugin_name)
            plugin_config = config.plugins.get(plugin_name, {})
            plugin = plugin_class(knotc_socket=args.socket,
                                  config=plugin_config)
            plugin.exec()
    except KeyboardInterrupt:
        log.error("Caught keyboard interrupt: aborting")
        return 130
    except Exception as e:
        log.error(f"An error occurred during execution: {e}")
        return 1
    return 0
