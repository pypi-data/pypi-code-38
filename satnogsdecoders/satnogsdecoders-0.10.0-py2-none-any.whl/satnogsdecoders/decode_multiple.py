"""
decode single (binary) frames from file or commandline
and multiple frames from a CSV file
"""

from __future__ import print_function

import argparse
import binascii
import json
import re
import sys

import satnogsdecoders.decode_frame as decode_frame


def main():
    """
    main entry point
    """

    parser = argparse.ArgumentParser(
        description='Decode single or multiple frames using a Kaitai'
        'Struct decoder into JSON objects.')
    parser.add_argument('decoder_name',
                        type=str,
                        help='Name of the decoder (e.g. Eshail2).')
    parser.add_argument('--filename',
                        type=str,
                        help='Filename containing the frame[s].')
    parser.add_argument('--hex_frame',
                        type=str,
                        help='Hexlified frame provided as argument like '
                        '"001122AABBCCDDEEFF".')
    parser.add_argument('--format',
                        type=str,
                        help='Input file format, \'bin\' or \'csv\'.')
    parser.add_argument('-v',
                        action="store_true",
                        help='Enables verbose output mode.')
    args = parser.parse_args()
    decode_multiple(args.decoder_name, args.filename, args.hex_frame,
                    args.format, args.v)


def decode_multiple(dname,
                    fname=None,
                    hframe=None,
                    fformat=None,
                    verbose=False):
    """
    Functional code goes here:
    """
    if fformat != 'bin' or fformat != 'csv':
        if hframe is not None:
            print("Wrong input file format! Must be 'bin' or 'csv'!",
                  file=sys.stderr)
            sys.exit(2)
    if fname is not None:
        if verbose is True:
            print('Input file is: {}'.format(fname), file=sys.stderr)
        if fformat == 'csv':
            lines = [line.rstrip('\n') for line in open(fname)]
            for each_line in lines:
                try:
                    # substitute newlines, " and carriage-return
                    each_line = re.sub('["\r\n]', '', each_line)
                    converted_line = binascii.unhexlify(each_line[20:])
                    if verbose == 1:
                        print("Decoding frame: {}\n".format(each_line[20:]),
                              file=sys.stderr)
                    fields = decode_frame.decode_frame(dname, converted_line)
                    print(json.dumps(fields, indent=4, sort_keys=False))
                except Exception as error:  # pylint: disable=broad-except
                    if verbose is True:
                        print("^~~~ Invalid frame!", file=sys.stderr)
                        print(error, file=sys.stderr)
        if fformat == 'bin':
            with open(fname, 'rb') as file_t:
                blob_data = bytearray(file_t.read())
                fields = decode_frame.decode_frame(dname, blob_data)
                print(json.dumps(fields, indent=4, sort_keys=False))
    if hframe is not None:
        frame = re.sub('["\r\n]', '', hframe)
        converted_line = binascii.unhexlify(frame)
        fields = decode_frame.decode_frame(dname, converted_line)
        print(json.dumps(fields, indent=4, sort_keys=False))
