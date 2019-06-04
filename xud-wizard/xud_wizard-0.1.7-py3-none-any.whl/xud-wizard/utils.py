import platform
import os
from .rpc.bitcoind import Bitcoind
from .rpc.lnd import Lnd
from .rpc.raiden import Raiden
from .rpc.xud import Xud
from .rpc.geth import Geth

# Hide CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
#   m.add_string(self.Q_C.public_numbers().encode_point())
# Ref. https://stackoverflow.com/a/55336269/2663029
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

prefix = "XUD_DOCKER_"

HOME = prefix + "HOME"
HOST = prefix + "HOST"


networks = {
    "regtest": {
        "services": {}
    },
    "simnet": {
        "services": {}
    },
    "testnet": {
        "services": {}
    },
    "mainnet": {
        "services": {}
    }
}


def print_services(title, services):
    c1w = max(len(title[0]), len(max(services.keys(), key=len)))
    c2w = max(len(title[1]), len(max(services.values(), key=len)))
    c1f = '{:' + str(c1w) + "}"
    c2f = '{:' + str(c2w) + "}"

    print(("┏━━" + c1f + "━━┯━━" + c2f + "━━┓").format("━" * c1w, "━" * c2w))
    print(("┃  " + c1f + "  │  " + c2f + "  ┃").format(title[0], title[1]))

    for key, value in services.items():
        print(("┠──" + c1f + "──┼──" + c2f + "──┨").format("─" * c1w, "─" * c2w))
        print(("┃  " + c1f + "  │  " + c2f + "  ┃").format(key, value))

    print(("┗━━" + c1f + "━━┷━━" + c2f + "━━┛").format("━" * c1w, "━" * c2w))


def get_home():
    """
    :return:
    Linux
        /home/<user>/.xud-docker
    Darwin (macOS)
        /Users/<user>/Library/Application Support/XudDocker
    Windows
        C:\\Users\\<user>\\AppData\\Local\\XudDocker
    """
    if HOME in os.environ:
        return os.environ[HOME]

    if platform.system() == 'Linux':
        return os.path.expanduser("~/.xud-docker")
    elif platform.system() == 'Darwin':
        return os.path.expanduser("~/Library/Application Support/XudDocker")
    elif platform.system() == 'Windows':
        return os.path.expanduser("~/AppData/Local/XudDocker")


def load_content(path):
    return open(path, 'rb').read()


def build_service(network, name):
    data = get_home() + ('/%s/data' % network)

    if name == 'bitcoind':
        connstr_bitcoind = "http://xu:xu@localhost:18332"
        s = Bitcoind(connstr_bitcoind)
    elif name == 'litecoind':
        connstr_litecoind = "http://xu:xu@localhost:19332"
        s = Bitcoind(connstr_litecoind)
    elif name == 'lndbtc':
        connstr_lndbtc = "localhost:10009"
        path_lndbtc_macaroon = data + ('/lndbtc/data/chain/bitcoin/%s/admin.macaroon' % network)
        path_lndbtc_cert = data + '/lndbtc/tls.cert'
        lndbtc_macaroon = load_content(path_lndbtc_macaroon)
        lndbtc_cert = load_content(path_lndbtc_cert)
        s = Lnd(connstr_lndbtc, lndbtc_cert, lndbtc_macaroon)
    elif name == 'lndltc':
        connstr_lndltc = "localhost:20009"
        path_lndltc_macaroon = data + ('/lndltc/data/chain/litecoin/%s/admin.macaroon' % network)
        path_lndltc_cert = data + '/lndltc/tls.cert'
        lndltc_macaroon = load_content(path_lndltc_macaroon)
        lndltc_cert = load_content(path_lndltc_cert)
        s = Lnd(connstr_lndltc, lndltc_cert, lndltc_macaroon)
    elif name == 'geth':
        connstr_geth = "http://localhost:8545"
        s = Geth(connstr_geth)
    elif name == 'raiden':
        connstr_raiden = "http://localhost:5001"
        s = Raiden(connstr_raiden)
    elif name == 'xud':
        connstr_xud = "localhost:8886"
        path_xud_cert = data + '/xud/tls.cert'
        xud_cert = load_content(path_xud_cert)
        s = Xud(connstr_xud, xud_cert)
    else:
        raise Exception('Unsupported service name: ' + name)

    return s


def get_service(network, name):
    if network not in networks:
        raise Exception("Unsupported network: %s" % network)
    services = networks[network]["services"]
    if name in services:
        return services[name]

    s = build_service(network, name)
    services[name] = s

    return s


