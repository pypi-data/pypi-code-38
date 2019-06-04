import argparse
import os
from .utils import get_home
import pathlib
import logging
import subprocess

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network", type=str, default='testnet', choices=['regtest', 'simnet', 'testnet', 'mainnet'])

    sub = parser.add_subparsers(dest="subparser")
    cmd_up = sub.add_parser("up")
    cmd_down = sub.add_parser("down")
    cmd_status = sub.add_parser("status")
    cmd_shell = sub.add_parser("shell")

    args = parser.parse_args()
    kwargs = vars(args)

    # Make sure docker is installed
    check_docker()

    # Make sure docker-compose is installed
    check_docker_compose()

    home = get_home() + "/" + args.network

    if not os.path.exists(home):
        pathlib.Path(home).mkdir(parents=True, exist_ok=True)

    if not os.path.isdir(home):
        logging.error("{} is not a directory", home)
        exit(1)

    # Go to xud-docker home directory
    os.chdir(home)

    globals()[kwargs.pop('subparser')](**kwargs)


if __name__ == '__main__':
    main()
