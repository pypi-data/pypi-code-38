from ivi_instruments import get_broadcasts, get_connected_vxi11_instruments


if __name__ == "__main__":
    print "get broadcasts..."
    print get_broadcasts()

    print "get connected vxi11 instruments..."
    print get_connected_vxi11_instruments()
