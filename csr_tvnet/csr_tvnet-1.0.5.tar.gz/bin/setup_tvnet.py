#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: RUN.PY


'''
import argparse
from csr_tvnet.csr_tvnet import csr_transit


def main(args):
    '''
    Main function involves taking care of:
             - Creating a local copy of the Custom Data file
            - Parsing the Custom data and creating data structure
    '''
    tvnet = csr_transit(customDataFileName=args.decoded,
                        configure_pubkey=args.configure_publickey,
                        username_pubkey=args.username_publickey,
                        private_storage_account=args.private_storage_account,
                        private_storage_key=args.private_storage_key)
    tvnet.configure_transit_vnet()
    tvnet.remove_eem_applet()

if __name__ == '__main__':  # pragma: no cover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--decoded',
        type=str,
        default="sampledecodedCustomData",
        help='File location for the decoded custom data')
    parser.add_argument(
        '-p',
        '--configure_publickey',
        action='store_true',
        help='Give this option to enable public key configure.')
    parser.add_argument(
        '-u',
        '--username_publickey',
        type=str,
        default='automate',
        help='Username for public key configuration. Default is automate')
    parser.add_argument(
        '-psa',
        '--private_storage_account',
        type=str,
        default=None,
        help='Name of the private storage account needed for saving PEM keys')
    parser.add_argument(
        '-psak',
        '--private_storage_key',
        type=str,
        default=None,
        help='Key of the private storage account needed for saving PEM keys')
    args = parser.parse_args()
    main(args)
