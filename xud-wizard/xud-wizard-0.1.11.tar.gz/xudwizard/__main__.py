import argparse
import os
from .utils import get_home
import pathlib
import logging
import subprocess
from . import config

logging.basicConfig(level=logging.INFO)

from .up import main as up
from .status import main as status
from .down import main as down
from .shell import main as shell


# os.chdir("/Users/yy/work/huiyin/xud-docker-dev/xud-testnet")
# os.system("docker-compose up -d")
#
# time.sleep(3)
#
# print(w3.eth.blockNumber)
# print(w3.eth.syncing)
# os.system("docker-compose down")
# os.system("docker-compose up -d geth")
# os.system("docker-compose exec -T geth geth --testnet --exec 'admin.nodeInfo' attach")
# os.system("docker-compose exec -T geth geth --testnet --exec 'eth.accounts' attach")
# os.system("docker-compose exec -T geth geth --testnet --exec 'eth.syncing' attach")
# os.system("docker-compose exec -T geth geth --testnet --exec 'eth.blockNumber' attach")
# os.system("docker-compose exec -T geth geth --testnet account list")
# os.system("docker-compose logs --tail=200 geth")
# output = subprocess.check_output("pwd")
# print(output)
# output = subprocess.check_output("docker-compose exec geth geth --testnet --help", shell=True)
# print(output)
# docker-compose exec geth geth --testnet attach
# personal.createAccount()


def check_docker():
    p = subprocess.Popen('which docker', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        logging.error("docker is missing")
        exit(1)
    # os.system('docker --version')


def check_docker_compose():
    p = subprocess.Popen('which docker', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        logging.error("docker-compose is missing")
        exit(1)
    # os.system('docker-compose --version')


def init_parser_with_config(parser):
    parser.add_argument("-n", "--network", type=str, default=config.network,
                        choices=['regtest', 'simnet', 'testnet', 'mainnet'])
    parser.add_argument("--bitcoind.address", type=str, default=config.bitcoind.address)
    parser.add_argument("--bitcoind.datadir", type=str, default=config.bitcoind.datadir)
    parser.add_argument("--litecoind.address", type=str, default=config.litecoind.address)
    parser.add_argument("--litecoind.datadir", type=str, default=config.litecoind.datadir)
    parser.add_argument("--lndbtc.address", type=str, default=config.lndbtc.address)
    parser.add_argument("--lndbtc.datadir", type=str, default=config.lndbtc.datadir)
    parser.add_argument("--lndltc.address", type=str, default=config.lndltc.address)
    parser.add_argument("--lndltc.datadir", type=str, default=config.lndltc.datadir)
    parser.add_argument("--geth.address", type=str, default=config.geth.address)
    parser.add_argument("--geth.datadir", type=str, default=config.geth.datadir)
    parser.add_argument("--raiden.address", type=str, default=config.raiden.address)
    parser.add_argument("--raiden.datadir", type=str, default=config.raiden.datadir)
    parser.add_argument("--xud.address", type=str, default=config.xud.address)
    parser.add_argument("--xud.datadir", type=str, default=config.xud.datadir)

    parser.add_argument("--host", type=str, default=config.host)


def update_config(args):
    config.network = args["network"]
    config.bitcoind.address = args["bitcoind.address"]
    config.bitcoind.datadir = args["bitcoind.datadir"]
    config.litecoind.address = args["litecoind.address"]
    config.litecoind.datadir = args["litecoind.datadir"]
    config.lndbtc.address = args["lndbtc.address"]
    config.lndbtc.datadir = args["lndbtc.datadir"]
    config.lndltc.address = args["lndltc.address"]
    config.lndltc.datadir = args["lndltc.datadir"]
    config.geth.address = args["geth.address"]
    config.geth.datadir = args["geth.datadir"]
    config.raiden.address = args["raiden.address"]
    config.raiden.datadir = args["raiden.datadir"]
    config.xud.address = args["xud.address"]
    config.xud.datadir = args["xud.datadir"]

    config.host = args["host"]


def main():
    parser = argparse.ArgumentParser()

    init_parser_with_config(parser)

    sub = parser.add_subparsers(dest="subparser")
    cmd_up = sub.add_parser("up")
    cmd_down = sub.add_parser("down")
    cmd_status = sub.add_parser("status")
    cmd_shell = sub.add_parser("shell")

    args = parser.parse_args()

    kwargs = vars(args)

    update_config(kwargs)

    # Make sure docker is installed
    #check_docker()

    # Make sure docker-compose is installed
    #check_docker_compose()

    # home = get_home() + "/" + args.network
    #
    # if not os.path.exists(home):
    #     pathlib.Path(home).mkdir(parents=True, exist_ok=True)
    #
    # if not os.path.isdir(home):
    #     logging.error("{} is not a directory", home)
    #     exit(1)
    #
    # # Go to xud-docker home directory
    # os.chdir(home)

    try:
        # globals()[kwargs.pop('subparser')](**kwargs)
        globals()[kwargs.pop('subparser')]()
    except KeyError:
        parser.print_help()


if __name__ == '__main__':
    main()
