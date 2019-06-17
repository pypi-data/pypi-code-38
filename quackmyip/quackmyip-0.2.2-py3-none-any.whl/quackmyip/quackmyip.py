
# Copyright 2019 by tuxedoar@gmail.com .

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from urllib.parse import urlencode
from datetime import datetime
from configparser import SafeConfigParser, NoOptionError, ParsingError
import sys
import argparse
import requests


def read_config_file(ini_file):
    """ Read configuration file """
    URL = {}
    parser = SafeConfigParser()
    # Check if config file exist
    if parser.read(ini_file):
        try:
            TOKEN = parser.get('duckdns', 'token')
            DOMAIN = parser.get('duckdns', 'domain')
            VERBOSE = "true"
            URL_BASE = "https://www.duckdns.org/update?"
            PARAMS = urlencode({'domains': DOMAIN, 'token': TOKEN, 'verbose': VERBOSE})
            URL['url'] = URL_BASE+PARAMS
            return URL['url']
        except (NoOptionError, ParsingError) as e:
            print("\n%s" % (e))
            sys.exit(1)
    else:
        print("\nERROR: Configuration file %s was not found!\n" % (ini_file))
        raise SystemExit


def send_request(URL):
    """ Setup the HTTP request to duckdns """
    HEADERS = {'user-agent': ''}
    response_data = []

    try:
        # Make a HTTP GET request
        r = requests.get(URL, verify=True, headers=HEADERS, timeout=3.0)
        response = r.text
        response_data.append(response)
        response_data = response_data[0].split('\n')
        # Filter empty strings in list
        response_data = list(filter(None, response_data))
        return response_data
    except requests.exceptions.RequestException as e:
        print("\n%s" % (e))
        sys.exit(1)


def process_http_response(response_data):
    """ Process the HTTP response """
    DATE_TIME = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    # Assign a name for each element of response
    if "OK" in response_data:
        for element in response_data:
            ip_addr, state = response_data[1], response_data[2]
        # if query_response == 'OK':
        if state == 'NOCHANGE':
            print("\n%s - Your IP %s has not changed. Nothing to update!.\n" % (DATE_TIME, ip_addr))
        elif state == 'UPDATED':
            print("\n%s - Your IP has been updated!. Your new IP is: %s .\n" % (DATE_TIME, ip_addr))
    # Assume query_response == 'KO':
    else:
        print("\nERROR: bad response recieved. Check your configuration file!.\n")


def get_args():
    """ Set arguments """
    parser = argparse.ArgumentParser(
        description='Update your IP address for your duckdns registered domain')
    parser.add_argument('FILE', help='The configuration file to use')

    args = parser.parse_args()
    return args


def main():
    """ Get arguments and call defined functions """
    sys.tracebacklimit = None
    args = get_args()
    URL = read_config_file(args.FILE)
    response_data = send_request(URL)
    process_http_response(response_data)

if __name__ == "__main__":
    main()
