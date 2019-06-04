from .utils import get_service


def main(network):
    from .utils import print_services

    bitcoind = get_service(network, 'bitcoind')
    litecoind = get_service(network, 'litecoind')
    xud = get_service(network, 'xud')
    lndbtc = get_service(network, 'lndbtc')
    lndltc = get_service(network, 'lndltc')
    geth = get_service(network, 'geth')
    raiden = get_service(network, 'raiden')

    title = ["SERVICE", "STATUS"]

    services = {
        "btc": bitcoind.status,
        "ltc": litecoind.status,
        "eth": geth.status,
        "lndbtc": lndbtc.status,
        "lndltc": lndltc.status,
        "raiden": raiden.status,
        "xud": xud.status,
    }

    print_services(title, services)




