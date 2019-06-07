import argparse
import os

from getmac import get_mac_address

from .connection import WSConnection, watch_for_collects, get_token, monitor


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('host', type=str, help='a hostname to make http and tcp requests',
                        nargs='?', default='localhost:8000')
    
    parser.add_argument('interface', type=str, help='internet interface used',
                        nargs='?', default='eth0')

    parser.add_argument('directory', type=str, help='directory where sensor data is saved',
                        nargs='?', default='~/ricc/data')
    
    args = parser.parse_args()

    mac_addr = get_mac_address(args.interface)
    
    if mac_addr:
        if not os.path.exists(args.directory):
            os.makedirs(args.directory)

        ws_url = 'ws://' + args.host + '/ws/?mac=' + mac_addr
        http_url = args.host + '/call'
        print('ws ', ws_url)
        print('http ', http_url)
        connection = WSConnection(ws_url, args.interface)
        connection.start_connection()
        monitor(args.directory, http_url, mac_addr)
    else:
        print("Invalid internet interface, couldn't get device mac address")
