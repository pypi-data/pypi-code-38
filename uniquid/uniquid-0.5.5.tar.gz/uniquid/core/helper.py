# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

"""Helper functions serving all modules.
"""

from operator import itemgetter


def parse_url(in_url, in_def_ip, in_def_port):
    """Parse a URL and extract the IP address and the port number.

    If the domain/IP address or port number is missing, use the default
    values.
    Arguments:
    in_url -- URL to be parsed.
    in_def_ip -- Default IP address to return. Must be a string.
    in_def_port -- Default port number to return. Must be a string.
    Returns:
    Returns a dictionary containing the IP address and port number.
    Throws:
    RuntimeError if an invalid default argument is passed to the function.
    """
    retval = {'ip': in_def_ip, 'port': in_def_port}
    tokens = []
    if (in_def_ip is None or
            in_def_port is None):
        raise RuntimeError('Internal. Null argument.')
    elif (not isinstance(in_def_ip, str) or
            not isinstance(in_def_port, str)):
        raise RuntimeError('Internal. Non-string argument.')
    if in_url:
        tokens = in_url.split(':')
    if len(tokens) > 1:
        # there was a colon in url
        if len(tokens[-1]) > 0:
            retval['port'] = tokens[-1]
        if len(tokens[-2]) > 0:
            retval['ip'] = tokens[-2].replace('/', '')
    elif (in_url and len(in_url) > 0):
        # no colon in url
        retval['ip'] = in_url.replace('/', '')
    return retval


def filter_list(in_list=None,
                in_key=None,
                in_value=None,
                in_is_case_sensitive=False,
                in_is_inclusive=False):
    """Filter a list of dictionaries based on the values of one field.

    A new list is returned and dictionaries are included in it if their field
    matches the specified value.  Inclusive matching means that dictionaries
    which are missing the field are also included in the returned list.
    Exclusive matching means that dictionaries which are missing the field are
    not included in the returned list.
    Arguments:
    in_list -- List of dictionary objects.
    in_key -- String name of the field.
    in_value -- Value the field should match.
    in_is_case_sensitive -- Boolean. True if filtering of values is case
    sensitive, otherwise False. Case insensitive by default.
    in_is_inclusive -- Boolean. True indicates that the matching should be
    inclusive, otherwise there is exclusive matching.
    Returns:
    A list of dictionary objects or an empty list.
    Throws:
    RuntimeError if an incorrect argument is passed.
    """
    retval = list()
    if not isinstance(in_list, list):
        raise RuntimeError('Internal. Incorrect argument type for in_list.')
    if (not in_key or
            not isinstance(in_key, str) or
            len(in_key) < 1):
        raise RuntimeError('Internal. Incorrect argument in_key.')
    if (not in_value or
            len(in_value) < 1):
        raise RuntimeError('Internal. Incorrect argument in_value.')
    for obj in in_list:
        if not isinstance(obj, dict):
            raise RuntimeError('Internal. List must contain dict objects.')
        if ((in_key in obj and
                ((in_is_case_sensitive and
                  obj[in_key] == in_value) or
                 ((not in_is_case_sensitive and
                   obj[in_key].lower() == in_value.lower())))) or
            (in_key not in obj and
                in_is_inclusive)):
            retval.append(obj)
    return retval


def sort_list(in_list=None,
              in_key=None,
              in_is_ascending=True,
              in_is_inclusive=True):
    """Sort a list of dictionaries based on the values of one field.

    A new list is returned and all of the dictionaries are included in it, in
    either ascending or descending order.  Inclusive matching means that
    dictionaries which are missing the field are also included in the
    returned list. Exclusive matching means that dictionaries which are missing
    the field are not included in the returned list.
    Arguments:
    in_list -- List of dictionary objects.
    in_key -- String name of the field.
    in_is_ascending -- True for ascending order, False for descending order.
    in_is_inclusive -- Boolean. True indicates that the sorting should be
    inclusive, otherwise dictionaries which are missing the key are
    excluded from the returned list.
    Returns:
    A list of dictionary objects or an empty list.
    Throws:
    RuntimeError if an incorrect argument is passed.
    """
    retval = list()
    missing_key = list()
    sort_list = list()
    if not isinstance(in_list, list):
        raise RuntimeError('Internal. Incorrect argument type for in_list.')
    if (not in_key or
            not isinstance(in_key, str) or
            len(in_key) < 1):
        raise RuntimeError('Internal. Incorrect argument in_key.')
    for item in in_list:
        if not isinstance(item, dict):
            raise RuntimeError('Internal. List must contain dict objects.')
        if in_key in item:
            sort_list.append(item)
        if (in_key not in item and
                in_is_inclusive):
            missing_key.append(item)
    if len(sort_list) > 0:
        sort_list = sorted(sort_list,
                           key=itemgetter(in_key),
                           reverse=not in_is_ascending)
    retval.extend(sort_list)
    retval.extend(missing_key)
    return retval
