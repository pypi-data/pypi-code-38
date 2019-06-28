#!/usr/bin/python3

import os
import sys
import time
import argparse
import logging
import coloredlogs
import pprint

import lerc_api

from configparser import ConfigParser

# configure logging #
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
# set noise level
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('lerc_api').setLevel(logging.INFO)

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)


def upgrade_host(hostname, upgrade_bat_path, lerc_msi_path):
    """Have a lerc upgrade itself to a newer version.

    :param str hostname: The hostname to issue upgrade commands.
    :param str upgrade_bat_path: Path to the upgrade.bat file used to manage the bootstrapped upgrade.
    :param str lerc_msi_path: Path to the current version of the lerc we're upgrading the client to.

    Upgrade Steps:

      #. Drop lercSetup.msi
      #. Drop upgrade.bat 
      #. Execute upgrade.bat async=True with correct params ex. -> upgrade.bat 0 15 2048 "https://your-server-address/"  -> company=0 reconnectdelay=15 chunksize=2048 serverurls="https://your-server-address/"
      #. Issue Quit command to host
    """

    host_commands = []

    ls = lerc_api.lerc_session()
    host = ls.get_host(hostname)
    if not host:
        logging.error("'{}' does not exist.".format(hostname))
        return "ERROR: '{}' does not exist.".format(hostname)
    logger = logging.getLogger(__file__+".upgrade_host")
    logger.info("Issuing upgrade commands to {}".format(hostname))

    # delete any existing lercSetup.msi that might already be on the host
    result = host.Run("DEL lercSetup.msi")
    host_commands.append(result)

    file_name = lerc_msi_path[lerc_msi_path.rfind('/')+1:]
    result = host.Download(file_name, client_file_path=file_name, analyst_file_path=lerc_msi_path)
    host_commands.append(result)

    file_name = upgrade_bat_path[upgrade_bat_path.rfind('/')+1:]
    result = host.Download(file_name, client_file_path=file_name, analyst_file_path=upgrade_bat_path)
    host_commands.append(result)

    run_cmd = config['default']['upgrade_cmd']
    result = host.Run(run_cmd.format(host.id), async=True)
    host_commands.append(result)

    result = host.Quit()
    host_commands.append(result)
    return host_commands


def compare_version_strings(client, production_lerc_version):
    """Check the version string the server has on a client with the current production version string. Note: version format  is #.#.#.#

    :param dict client: A client dictionary obtained from the lerc server.
    :param str production_lerc_version: A string representation of the current production lerc version.
    :return: True if the client version is older than the production version; False if equal or greater.
    """
    logger = logging.getLogger(__name__+".compare_versions")
    logger.debug("Version comparision : Client Current Version={} - Production Version={}".format(client.version, production_lerc_version))
    production_lerc_version_str = production_lerc_version
    production_lerc_version = production_lerc_version.split('.')
    if client.version == production_lerc_version_str:
        logger.warn("Client '{}' is already at the current production version '{}'".format(client.hostname, production_lerc_version_str))
        return False
    else:
        client_ver = client.version.split('.')
        if len(client_ver) != len(production_lerc_version):
            logger.warn("Version annomoly on {} - client version:{} and production version:{}".format(client.hostname, client.version, production_lerc_version_str))
            return False
        for i in range(len(client_ver)):
            if client_ver[i] < production_lerc_version[i]:
                return True
        else:
            logger.error("Client version:{} greater than production_lerc_version:{}. Is your configuration wrong?".format(client.version, production_lerc_version_str))
            return False


if __name__ == "__main__":

    config = lerc_api.load_config(required_keys=['upgrade_cmd', 'upgrade_bat', 'client_installer', 'production_lerc_version'])
    env_choices = [c for c in config.sections() if 'default' not in c and '_' not in c]

    parser = argparse.ArgumentParser(description="A script to upgrade clients with a new lerc version.")
    parser.add_argument('-f', '--file', action="store", help="specify the path to a lercSetup.msi (default used from config file)")
    parser.add_argument('-d', '--debug', action="store_true", help="set logging to DEBUG")
    parser.add_argument('-e', '--environment', choices=env_choices, action='store', help="only upgrade hosts in a certain environment.")
    parser.add_argument('-c', '--client-hostname', action='store', help="upgrade this specific client, only")
    parser.add_argument('--force', action='store_true', help="make the client upgrade regardless of any other conditions, such as production_lerc_version")
    parser.add_argument('--write-commands', action='store_true', help="write all of the issued commands to a file for future reference.")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger('lerc_api').setLevel(logging.DEBUG)
        coloredlogs.install(level='DEBUG', logger=logger)
        logger.setLevel(logging.DEBUG)

    upgrade_bat_path = lerc_msi_path = production_lerc_version = company_id = None
    # It's possible different environments have different requirements
    if args.environment:
        if config.has_option(args.environment, 'upgrade_bat'):
            upgrade_bat_path = config[args.environment]['upgrade_bat']
        if config.has_option(args.environment, 'client_installer'):
            lerc_msi_path = config[args.environment]['client_installer']
        if config.has_option(args.environment, 'production_lerc_version'):
            production_lerc_version = config[args.environment]['production_lerc_version']
        if config.has_option(args.environment, 'company_id'):
            company_id = config[args.environment].getint('company_id')

    # defaults
    if upgrade_bat_path is None:
        upgrade_bat_path = config['default']['upgrade_bat']
    if lerc_msi_path is None:
        lerc_msi_path = config['default']['client_installer']
    if production_lerc_version is None:
        production_lerc_version = config['default']['production_lerc_version']

    logger.debug("upgrade_bat_path: {}".format(upgrade_bat_path))
    logger.debug("lerc_msi_path: {}".format(lerc_msi_path))
    logger.debug("production_lerc_version: {}".format(production_lerc_version))

    # check paths
    for path in [upgrade_bat_path, lerc_msi_path]:
        if not os.path.exists(path):
            logger.error("Does not exist: {}".format(path))
            sys.exit(1)

    ls = lerc_api.lerc_session()

    if args.client_hostname:
        client = ls.get_host(args.client_hostname)
        if not client:
            logger.error("Client doesn't exist")
            sys.exit(1)
        # make sure this host's company_id matches what we have for this environment
        if args.environment:
            if company_id is None:
                logger.error("Company id is not specified in the configuration for '{}'".format(args.environment))
                sys.exit(1)
            elif company_id != int(client.company_id):
                logger.warn("Client company id and company id for '{}' do not match. Wrong hostname?".format(args.environment))
                sys.exit(1)
        if not args.force:
            # check lerc version strings
            if client.version is not None:
                proceed = compare_version_strings(client, production_lerc_version)
                if not proceed: # we exit since we're only working on one host
                    sys.exit(1)
        commands = upgrade_host(args.client_hostname, upgrade_bat_path, lerc_msi_path)
        if args.write_commands:
            with open(args.client_hostname+"_upgrade.log", 'w') as fh:
                fh.write(pprint.pformat(commands))
            print("Wrote client upgrade commands to '{}'".format(args.client_hostname+"_upgrade.log"))
        sys.exit()

    host_commands = {}
    for host in ls.yield_hosts():
        if host.hostname == 'WIN-1TMIV79KTI8' or host.hostname == 'icinga' \
                                                 or host.hostname == 'W7GOTCHAPC':
            continue
        if args.environment:
            if company_id is None:
                logger.error("Company id is not specified in the configuration for '{}'".format(args.environment))
                sys.exit(1)
            elif company_id != int(host.company_id):
                logger.debug("Client company id and company id for '{}' do not match for {}/{}".format(args.environment, host.hostname, host.id))
                continue
        if host.status != 'UNINSTALLED':
            if not compare_version_strings(host, production_lerc_version):
                continue
            host_commands[host.hostname] = upgrade_host(host.hostname, upgrade_bat_path, lerc_msi_path)

    if args.write_commands:
        with open("lerc_upgrade_commands.txt", 'w') as fh:
            fh.write(pprint.pformat(host_commands))
        print("Wrote lerc_upgrade_commands.txt.")

    sys.exit()
