#!/usr/bin/env python3

"""
Send a test email using the mail configuration in the user-provided configuration file. 
"""

import argparse

from sruns_monitor.monitor import Monitor


def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
    parser.add_argument("-c", "--conf-file", required=True, help="The JSON configuration file.")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    conf_file = args.conf_file
    m = Monitor(conf_file=conf_file)
    if not m.get_mail_params():
        # mail isn't configured in the conf file that the user provided
        raise Exception("You must provided mail configuration in your conf file.")
    m.send_mail(subject="sruns-mon test email", msg_body="test")

if __name__ == "__main__":
    main()



