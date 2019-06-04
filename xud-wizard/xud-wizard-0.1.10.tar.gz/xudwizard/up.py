import threading
import os
from .utils import get_service
import pexpect
import logging
import urllib.request
from .down import main as down
from .shell import main as shell
import subprocess

btc_ok = False
ltc_ok = False
eth_ok = False

btc_stop_event = threading.Event()
ltc_stop_event = threading.Event()
eth_stop_event = threading.Event()


def expect(cmd):
    return pexpect.spawn(cmd)


def wait_bitcoind_synced(network):
    bitcoind = get_service(network, 'bitcoind')
    status = bitcoind.status
    while status != "OK":
        print('[BTC] bitcoind: ' + status)
        btc_stop_event.wait(30)
        if btc_stop_event.is_set():
            raise Exception("bitcoind waiting interrupted")
        status = bitcoind.status


def wait_litecoind_synced(network):
    litecoind = get_service(network, 'litecoind')
    status = litecoind.status
    while status != "OK":
        print('[LTC] litecoind: ' + status)
        ltc_stop_event.wait(30)
        if ltc_stop_event.is_set():
            raise Exception("litecoind waiting interrupted")
        status = litecoind.status


def wait_geth_synced(network):
    geth = get_service(network, 'geth')
    status = geth.status
    while status != "OK":
        print('[ETH] geth: ' + status)
        eth_stop_event.wait(30)
        if eth_stop_event.is_set():
            raise Exception("geth waiting interrupted")
        status = geth.status


def docker_compose_up(service):
    p = subprocess.Popen('docker-compose up -d ' + service, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        logging.error("Failed to start up service: %s (%s)", service, stderr)
        exit(1)


def create_lnd_wallet(network, chain, password):
    service = None
    if chain == 'bitcoin':
        service = 'lndbtc'
    elif chain == 'litecoin':
        service = 'lndltc'
    child = expect("docker-compose exec {} lncli -n {} -c {} create".format(service, network, chain))
    child.expect('Input wallet password: ')
    child.sendline(password)
    child.expect('Confirm wallet password: ')
    child.sendline(password)
    # Do you have an existing cipher seed mnemonic you want to use? (Enter y/n):
    child.expect("Do you have an existing cipher seed mnemonic you want to use")
    child.sendline("n")
    # Input your passphrase if you wish to encrypt it (or press enter to proceed without a cipher seed passphrase):
    child.expect("Input your passphrase if you wish to encrypt it")
    child.sendline()
    # Generating fresh cipher seed...
    #
    # !!!YOU MUST WRITE DOWN THIS SEED TO BE ABLE TO RESTORE THE WALLET!!!
    #
    # ---------------BEGIN LND CIPHER SEED---------------
    #  1. abandon   2. ride      3. shine     4. return
    #  5. twelve    6. receive   7. promote   8. hood
    #  9. nut      10. upset    11. pave     12. tag
    # 13. note     14. glory    15. violin   16. borrow
    # 17. slush    18. square   19. country  20. outdoor
    # 21. garment  22. clutch   23. grocery  24. rotate
    # ---------------END LND CIPHER SEED-----------------
    #
    # !!!YOU MUST WRITE DOWN THIS SEED TO BE ABLE TO RESTORE THE WALLET!!!
    #
    # lnd successfully initialized!
    child.expect("lnd successfully initialized")

    if child.isalive():
        child.close()


def unlock_lnd_wallet(network, chain, password):
    service = None
    if chain == 'bitcoin':
        service = 'lndbtc'
    elif chain == 'litecoin':
        service = 'lndltc'
    child = expect("docker-compose exec {} lncli -n {} -c {} unlock".format(service, network, chain))
    child.expect('Input wallet password: ')
    child.sendline(password)
    # lnd successfully unlocked!
    # [lncli] rpc error: code = Unknown desc = wallet not found
    r = child.expect(['lnd successfully unlocked', 'rpc error'])

    if child.isalive():
        child.close()

    if r == 0:
        logging.info("%s wallet unlocked", service)
    else:
        raise Exception("Failed to unlock %s wallet: %s", service, child.match)


def up_btc(network):
    global btc_ok
    try:
        docker_compose_up("bitcoind")
        wait_bitcoind_synced(network)
        print("[BTC] Layer 1 node is ready")

        docker_compose_up("lndbtc")

        log = expect('docker-compose logs -f lndbtc')
        # [INF] LTND: Waiting for wallet encryption password. Use `lncli create` to create a wallet, `lncli unlock` to unlock an existing wallet, or `lncli changepassword` to change the password of an existing wallet and unlock it.
        log.expect('Waiting for wallet encryption password')

        password_path = "lndbtc-password.txt"

        if not os.path.exists(password_path):
            password = '12345678'
            with open(password_path, 'w') as f:
                f.write(password)
            create_lnd_wallet(network, "bitcoin", password)

        password = open(password_path).read()

        # unlock wallets
        unlock_lnd_wallet(network, "bitcoin", password)

        # validate lndbtc started
        # [INF] RPCS: RPC server listening on 0.0.0.0:10009
        log.expect('RPC server listening on', timeout=300)

        if log.isalive():
            log.close()

        print("[BTC] Layer 2 node is ready")

        btc_ok = True
    except Exception as e:
        raise Exception("Failed to start up btc", e)


def up_ltc(network):
    global ltc_ok
    try:
        ltc_stop_event.wait(2)
        docker_compose_up("litecoind")
        wait_litecoind_synced(network)
        print("[LTC] Layer 1 node is ready")

        docker_compose_up("lndltc")

        log = pexpect.spawn('docker-compose logs -f lndltc')

        # [INF] LTND: Waiting for wallet encryption password. Use `lncli create` to create a wallet, `lncli unlock` to unlock an existing wallet, or `lncli changepassword` to change the password of an existing wallet and unlock it.
        log.expect('Waiting for wallet encryption password')

        password_path = "lndltc-password.txt"

        if not os.path.exists(password_path):
            password = '12345678'
            with open(password_path, 'w') as f:
                f.write(password)
            create_lnd_wallet(network, "litecoin", password)

        password = open(password_path).read()

        # unlock wallets
        unlock_lnd_wallet(network, "litecoin", password)

        # validate lndbtc started
        # [INF] RPCS: RPC server listening on 0.0.0.0:10009
        log.expect('RPC server listening on', timeout=300)

        if log.isalive():
            log.close()

        print("[LTC] Layer 2 node is ready")

        ltc_ok = True
    except Exception as e:
        raise Exception("Failed to start up ltc", e)


def create_geth_wallet(network):
    # docker-compose exec geth geth --testnet account new
    # INFO [05-29|18:42:10.653] Maximum peer count                       ETH=50 LES=0 total=50
    # Your new account is locked with a password. Please give a password. Do not forget this password.
    # Passphrase:
    # Repeat passphrase:
    #
    # Your new key was generated
    #
    # Public address of the key:   0x2400A197137c74D5403F4A0e5d7abC4a07469F0e
    # Path of the secret key file: /root/.ethereum/testnet/keystore/UTC--2019-05-29T18-42-23.086966945Z--2400a197137c74d5403f4a0e5d7abc4a07469f0e
    #
    # - You can share your public address with anyone. Others need it to interact with you.
    # - You must NEVER share the secret key with anyone! The key controls access to your funds!
    # - You must BACKUP your key file! Without the key, it's impossible to access account funds!
    # - You must REMEMBER your password! Without the password, it's impossible to decrypt the key!

    # docker-compose exec geth geth --testnet account list
    # INFO [05-29|18:43:52.225] Maximum peer count                       ETH=50 LES=0 total=50
    # WARN [05-29|18:43:52.226] Failed to start smart card hub, disabling: dial unix /run/pcscd/pcscd.comm: connect: no such file or directory
    # Account #0: {d749fa6626c6489c05d8b575a477f02511f43d08} keystore:///root/.ethereum/testnet/keystore/UTC--2019-05-20T06-01-59.648910300Z--d749fa6626c6489c05d8b575a477f02511f43d08
    # Account #1: {2400a197137c74d5403f4a0e5d7abc4a07469f0e} keystore:///root/.ethereum/testnet/keystore/UTC--2019-05-29T18-42-23.086966945Z--2400a197137c74d5403f4a0e5d7abc4a07469f0e

    if os.path.exists(".env"):
        env = open('.env').read()
        if 'GETH_ACCOUNT' in env:
            return

    account = None
    passphrase = ''

    child = pexpect.spawn('docker-compose exec geth geth --testnet account new')
    child.expect('Passphrase: ')
    child.sendline(passphrase)
    child.expect('Repeat passphrase: ')
    child.sendline(passphrase)

    child.expect(r'Public address of the key:\s+(\w+)')
    account = child.match.group(1).decode()

    logging.info("New geth account is %s" % account)

    if child.isalive():
        child.close()

    with open('.env', 'w') as f:
        f.write('GETH_ACCOUNT=%s' % account)

    p = subprocess.Popen("docker-compose exec geth sh -c 'echo %s > /root/.ethereum/passphrase.txt'" % passphrase, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        raise Exception("Failed to write geth passphrase into a file: %s" % stderr)


def up_eth(network):
    global eth_ok
    try:
        eth_stop_event.wait(4)
        docker_compose_up("geth")
        wait_geth_synced(network)
        print("[ETH] Layer 1 node is ready")
        create_geth_wallet(network)
        docker_compose_up("raiden")
        print("[ETH] Layer 2 node is ready")
        eth_ok = True
    except Exception as e:
        raise Exception("Failed to start up eth", e)


def up_xud(network):
    try:
        docker_compose_up("xud")
        print("Xud is ready")
    except Exception as e:
        raise Exception("Failed to start up xud", e)


def download_docker_compose_yaml_file(network):
    # download docker-compose.yml
    url = "https://raw.githubusercontent.com/ExchangeUnion/xud-docker/master/xud-{}/docker-compose.yml".format(network)
    urllib.request.urlretrieve(url, 'docker-compose.yml')
    logging.info("Downloaded docker-compose.yml")


def init(network):
    t1 = threading.Thread(target=up_btc, args=(network,))
    t2 = threading.Thread(target=up_ltc, args=(network,))
    t3 = threading.Thread(target=up_eth, args=(network,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    if btc_ok and ltc_ok and eth_ok:
        up_xud(network)
    else:
        raise Exception("Failed to init btc_ok=%s, ltc_ok=%s, eth_ok=%s" % (btc_ok, ltc_ok, eth_ok))


def pull_latest_images():
    p = subprocess.Popen('docker-compose pull', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise Exception("Failed to pull latest images: %s" % stderr)
    logging.info("Pulled latest images")


def main(network):
    try:
        down(network)
        download_docker_compose_yaml_file(network)
        pull_latest_images()
        init(network)
        shell(network)
    except KeyboardInterrupt:
        btc_stop_event.set()
        ltc_stop_event.set()
        eth_stop_event.set()




