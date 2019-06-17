# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import collections

import ipaddress
import re
import urllib.parse

from steelscript.cmdline import exceptions

"""
CLI parsers for the Riverbed appliance CLI

This module is a collection of parser functions designed to reduce code
duplication in model methods, and other methods which interact with the
CLI on Riverbed appliances.

All parsers should be written as functions with no state.  When performing
more complicated parsing operations it should be preferred to chain together
independent parsing actions.

Where parsing actions do not exist for specific CLI outputs, it
should be considered whether a new generic parser should be added or if
specific one off logic should be implemented in the model method
"""

CONST_RESTART_REQUIRED = ["<<Service needs a 'restart' for this \
config to take effect>>", "You must restart the service for your changes \
to take effect.", "You must restart the optimization service for your changes \
to take effect."]

CONST_REBOOT_REQUIRED = ["Please save your configuration and reboot the \
appliance for your changes to take effect."]


def cli_parse_basic(input_string):
    """
    Standard cli parsers for ``key: value`` style

    This parser goes through all the lines in the input string and returns a
    dictionary of parsed output.  In addition to splitting the output into
    key value pairs, the values will be fed through parse_boolean to turn
    strings such as ``yes`` and ``true`` into boolean objects, leaving other
    strings alone.

    This function will parse cli commands such as::

        hw1-int1 (config) # show load balance fair-peer-v2
        Fair peering V2: yes
        Threshold:       15 %

    creating a dictionary:

    .. code-block:: python

        {
            'fair peering v2': True,
            'threshold' : '15 %'
        }

    For this example one would want to perform further manipulation on the
    dictionary to get it into a usable state, changing ``fair peering v2`` to
    ``enabled`` and ``15 %`` to ``15`` for threshold.
    See :func:`enable_squash` for part of this.

    :param input_string: A string of CLI output to be parsed
    :return: a dictionary of parsed output
    """
    parsed_output = {}
    lines = (line for line in input_string.splitlines() if ':' in line)
    for line in lines:
        key, value = line.split(':', 1)

        key = key.strip().lower()
        if key in parsed_output:
            raise KeyError('Duplicate key exists')

        value = value.strip()
        try:
            parsed_output[key] = parse_boolean(value)
        except ValueError:
            value = check_numeric(value)
            if value == '':
                value = None
            parsed_output[key] = value
    return parsed_output


def cli_parse_table(input_string, headers):
    """
    Parser for Generic Table style output.  More complex tables outputs
    may require a custom parser.

    Parses output such as::

      Destination       Mask              Gateway           Interface
      10.3.0.0          255.255.248.0     0.0.0.0           aux
      default           0.0.0.0           10.3.0.1

    The left/right bounds of each data field are expected to fall underneath
    exactly 1 header.  If a data item falls under none or more than 1, an
    error will be raised.

    Data fields are initially divided by 2 spaces.  This allows single spaces
    within the data fields.  However, if the data crosses more than 1 header,
    it is then divided by single spaces and each piece will be part of whatever
    header it falls under.  If any part doesn't fall underneath a header, an
    error is raised.

    The example output above would produce the following structure:

    .. code-block:: python

        [
            {
                destination: 10.3.0.0,
                mask: 255.255.248.0,
                gateway: 0.0.0.0,
                interface: aux
            },
            {
                destination: default,
                mask: 0.0.0.0,
                gateway: 10.3.0.1
            },
        ]

    :param input_string: A string of CLI output to be parsed
    :param headers: array of headers in-order starting from the left.
    :return: an array of dictionaries of parsed output
    """
    parsed_output = []

    # Sanitize headers.  Lowercase and must all be unique
    headers = [x.lower() for x in headers]
    if len(headers) != len(set(headers)):
        raise ValueError("You cannot have duplicate headers!")

    lines = (x for x in input_string.splitlines() if re.search(r'\w', x))

    # Validate the header
    header_line = next(lines).lower()
    if not all(x in header_line for x in headers):
        raise exceptions.UnexpectedOutput('Unknown', header_line,
                                          expected_output=True,
                                          notes=["not all headers found "
                                                 "in: '%s'" % header_line])

    # Get the header 'domains' (left,right indexes) for each header.
    last_index = 0
    domains = []
    for header in headers:
        header_left = header_line.index(header, last_index)
        header_right = header_left + len(header)
        domains.append((header_left, header_right))
        last_index = header_right

    Column = collections.namedtuple('Column', 'data, left, right')

    # Now we have the domain for each header.  We require that each data item
    # falls within exactly 1 header domain, else we can't know where it belongs
    for line in lines:
        # array of namedtuples with data, start index, and end index.
        # e.g (data="Column", left=0, right=5)
        columns = [Column(m.group(0), m.start(), m.end()-1)
                   for m in re.finditer(r'(?:\S\s\S|\S)+', line)]

        # Data items with 2 spaces are definitely different columns; however,
        # if we get a conflict, we split for every space and divide each item
        # into what domain it best matches.  We then append the items within
        # a domain into 1 item.  If some item crosses 2 domains, Error out.
        row = {}
        for column in columns:
            # Check if this crosses only 1 header domain.  left index would be
            # less than the right bounds of headerX and right index would be
            # greater than the left bounds of headerX+1 if crossing 2+ headers.
            (leftmost, rightmost) =\
                _find_left_right_headers(left_index=column.left,
                                         right_index=column.right,
                                         domains=domains)

            if leftmost < rightmost:
                # Splitting with double spaces spanned too many columns, split
                # into single-spaced strings and try again.
                extra_words = [Column(m.group(0), m.start(), m.end()-1)
                               for m in re.finditer(r'\S+', column.data)]
                for word in extra_words:
                    # We have to add column.left to get the position
                    # in the original string.
                    (word_leftmost, word_rightmost) =\
                        _find_left_right_headers(
                            left_index=word.left + column.left,
                            right_index=word.right + column.left,
                            domains=domains)

                    if word_leftmost < word_rightmost:
                        raise exceptions.UnexpectedOutput(
                            'Unknown', '%s\n%s' % (header_line, line),
                            expected_output=True,
                            notes=["Data item '%s' crosses headers "
                                   "'%s' and '%s'." % (column.data,
                                                       headers[leftmost],
                                                       headers[rightmost]),
                                   "Word '%s' crosses headers "
                                   "'%s' and '%s'" % (word.data,
                                                      headers[word_leftmost],
                                                      headers[word_rightmost])]
                            )
                    if word_leftmost > word_rightmost:
                        raise exceptions.UnexpectedOutput(
                            'Unknown', '%s\n%s' % (header_line, line),
                            expected_output=True,
                            notes=["Data item '%s' crosses headers "
                                   "'%s' and '%s'." % (column.data,
                                                       headers[leftmost],
                                                       headers[rightmost]),
                                   "Word '%s' does not fall under a header" %
                                   word.data])

                    # This word falls under 1 header, we append all the
                    # words together that fall under 1 header.
                    key = headers[word_leftmost].lower()
                    if key in row:
                        row[key] += " " + word.data
                    else:
                        row[key] = word.data

            elif leftmost > rightmost:
                # This data item didn't fall within any header
                raise exceptions.UnexpectedOutput(
                    'Unknown', '%s\n%s' % (header_line, line),
                    expected_output=True,
                    notes=["Data item '%s' does not fall under a header" %
                           column.data])
            else:
                # Now we know this data item crosses 1 header.
                key = headers[leftmost].lower()
                if key in row:
                    raise exceptions.UnexpectedOutput(
                        'Unknown', '%s\n%s' % (header_line, line),
                        expected_output=True,
                        notes=["Multiple items under the same header: "
                               "'%s' and '%s'" % (row[key], column.data)])
                else:
                    row[key] = column.data

        parsed_output.append(row)
    return parsed_output


def _find_left_right_headers(left_index, right_index, domains):
    # Find the leftmost and rightmost matching header.
    # leftmost = first header with a right index > column's left index.
    # similarly for rightmost, only we must reverse the list.
    leftmost = next((x[0] for x in enumerate(domains) if left_index < x[1][1]),
                    len(domains))
    rightmost = next((x[0] for x in reversed(list(enumerate(domains)))
                     if right_index > x[1][0]), -1)
    return leftmost, rightmost


def check_numeric(value_string):
    """
    This function tries to determine if a string would be better represented
    with a numeric type, either int or float.  If neither works, for example
    ``10 Mb``, it will simply return the same string provided

    :param value_string: input string to be parsed.

    :return: the input string, an int, or a float
    """
    if type(value_string) in ('int', 'long', 'float'):
        return value_string

    try:
        if '.' in value_string:
            return float(value_string)
    except (TypeError, ValueError):
        pass

    try:
        return int(value_string)
    except (TypeError, ValueError):
        pass

    return value_string


def enable_squash(input):
    """
    Convert long specific enable strings to 'enabled'

    Takes in a dictionary of parsed output, iterates over the keys and looks
    for key names containing the string "enabled" at the end of the key name.
    Specifically the end of the key name is matched for safety.  Replaces the
    key with simply "enabled", for example an input dictionary::

        {"Path-selection enabled": False}

    becomes::

        {"enabled": False}

    :param input: A dictionary of parsed output
    :return result: A dictionary with keys ending in "enabled" replaced with
                    just "enabled"
    """
    result = {}
    for key, value in input.items():
        if key.endswith('enabled'):
            if 'enabled' in result:
                raise KeyError('Duplicate key exists')
            result['enabled'] = value
        else:
            result[key] = value

    return result


def parse_boolean(value_string):
    """
    Determine the boolean value of the input string.

    "yes", "no", "true" and "false" are recognized (case-insensitive).

    :param value_string: input string to be parsed.

    :return: boolean value based on input string
    :raises ValueError: if the string is not recognized as a boolean
    """
    value_string = value_string.lower().strip()
    if value_string in ("yes", "true"):
        return True
    if value_string in ("no", "false"):
        return False
    raise ValueError("Invalid value for conversion: " + value_string)


def restart_required(input):
    """
    Take result from a cli command and check if a service restart
    is required. Return True if cli result indicates restart required

    :param input: result from a cli command

    :rtype: bool
    """

    output = False

    # If there is no input, there is nothing to do here
    if input is None:
        return output

    lines = (line.strip() for line in input.splitlines() if line)
    for line in lines:
        if line in CONST_RESTART_REQUIRED:
            output = True
            break

    return output


def reboot_required(input):
    """
    Take result from a cli command and check if a reboot
    is required. Return True if cli result indicates reboot required

    :param input: result from a cli command

    :rtype: bool
    """

    output = False

    # If there is no input, there is nothing to do here
    if input is None:
        return output

    lines = (line.strip() for line in input.splitlines() if line)
    for line in lines:
        if line in CONST_REBOOT_REQUIRED:
            output = True
            break

    return output


def parse_ip_and_port(input):
    """
    Parse IP and Port number combo to a dictionary::

        1.1.1.1:2000

    to:

    .. code-block:: python

        {'ip': IPv4Address('1.1.1.1'), 'port': 2000}

    :param string input: IP and port

    :return: dictionary with keys ``ip`` and ``port``
    """
    ip_port_dict = {}
    address, port = input.split(':')
    ip_port_dict['ip'] = ipaddress.ip_address(address)
    ip_port_dict['port'] = port
    return ip_port_dict


def parse_url_to_host_port_protocol(input):
    """
    Parse url to a dictionary using :func:`urlparse.urlparse`,
    inferring the port from the scheme (a.k.a. protocol)::

       http://blah.com

    becomes:

    .. code-block:: python

        {'host': 'blah.com', 'port': 80, 'protocol': 'http'}

    :param string input: url

    :return: dict with port always specified
    """
    hpp_dict = {}
    url_object = urllib.parse.urlparse(input)
    protocol = url_object.scheme
    port = url_object.port
    host = url_object.hostname

    # urlparse does not infer port
    if not port:
        if protocol == "http":
            port = 80
        if protocol == "https":
            port = 443

    hpp_dict['host'] = host
    hpp_dict['port'] = port
    hpp_dict['protocol'] = protocol
    return hpp_dict


def parse_saasinfo_data(input):
    """
    Parse saasinfo data to a dictionary contained ip, port and geodns mapping
    data structures::

        =================================
        SaaS Application
        =================================
        SAMPLEAPP

        =================================
        SaaS IP
        =================================
        10.41.222.0/24 [0-65535]
        111.221.112.0/21 [1-65535]
        111.221.116.0/24 [1-65535]
        111.221.17.160/27 [1-65535]
        111.221.20.128/25 [0-65535]

        =================================
        SaaS Hostname
        =================================
        *.mail.apac.example.com
        *.example1.com
        *.example2.com
        example1.com

        =================================
        GeoDNS
        =================================
        ---------------------------------
        MBX Region
        ---------------------------------
        blu nam.ca.bay-area
        apc nam.ca.bay-area
        xyz nam.ca.bay-area
        abc nam.tx.san-antonio
        ---------------------------------
        Regional IPs
        ---------------------------------
        nam.ca.bay-area
        132.245.80.146
        132.245.80.150
        nam.tx.san-antonio
        132.245.80.153
        132.245.80.156
        132.245.81.114

    to:

    .. code-block:: python

        {
            'appid': 'SAMPLEAPP',
            'ip': [
                '10.41.222.0/24 [0-65535]',
                '111.221.112.0/21 [1-65535]',
                '111.221.116.0/24 [1-65535]',
                '111.221.17.160/27 [1-65535]',
                '111.221.20.128/25 [0-65535]',
            ],
            'host': [
                '*.mail.apac.example.com',
                '*.example1.com',
                '*.example2.com',
                'example1.com',
            ],
            'geodns': {
                'nam.ca.bay-area': {
                    'mbx': ['blu', 'apc', 'xyz'],
                    'ip': ['132.245.80.146', '132.245.80.150'],
                },
                'nam.tx.san-antonio': {
                    'mbx': ['abc'],
                    'ip': [
                        '132.245.80.153',
                        '132.245.80.156',
                        '132.245.81.114',
                    ]
                },
            },
        }

    :param string input: CLI output of saasinfo data

    :return: dictionary with saasinfo data as above
    """
    saasdata_dict = {}
    saasdata_dict['ip'] = []
    saasdata_dict['host'] = []
    saasdata_dict['geodns'] = {}
    lines = (line.rstrip() for line in input.splitlines())
    lines = (line for line in lines if line and not line[0] in '=-')
    section = None
    region = None
    for line in lines:
        if "SaaS Application" == line:
            section = "appid"
        elif "SaaS IP" == line:
            section = "ip"
        elif "SaaS Hostname" == line:
            section = "host"
        elif "MBX Region" == line:
            section = "mbx"
        elif "Regional IPs" == line:
            section = "region"
        elif "GeoDNS" == line:
            section = "geodns"
        else:
            if section == "appid":
                saasdata_dict['appid'] = line
            elif section == "ip" or section == "host":
                saasdata_dict[section].append(line)
            elif section == "mbx":
                (mbx, region) = line.split()
                if region not in saasdata_dict['geodns']:
                    saasdata_dict['geodns'][region] = {}
                    saasdata_dict['geodns'][region]['mbx'] = []
                    saasdata_dict['geodns'][region]['ip'] = []
                saasdata_dict['geodns'][region]['mbx'].append(mbx)
            elif section == "region":  # we're in region
                if line in saasdata_dict['geodns']:
                    region = line
                else:
                    # verify we have a valid ip address
                    ipaddress.ip_address(line)
                    saasdata_dict['geodns'][region]['ip'].append(line)
            else:
                raise KeyError('Unexpected SaaS Info data CLI output')
                # keyerror

    return saasdata_dict
