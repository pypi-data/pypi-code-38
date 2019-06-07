import argparse
import random
import re


class UnsupportedOperation(Exception):
    """
    Exception class for unsupported operations.
    """
    pass


def extract_alphanumeric(value):
    """
    Extract alphanumeric values from given string.

    :param value:
    :return:
    """
    pattern = re.compile('[\W_]+')
    return pattern.sub('', value)


def pair_hexvalue(value, delimiter=':'):
    """
    Pair hex values (string) using delimiter.
    e.g. abcdef -> ab:cd:ef

    :param value:
    :param delimiter:
    :return:
    """
    return delimiter.join(
        ['{}{}'.format(a, b) for a, b in zip(value[::2], value[1::2])])


def int_to_hexstr(value, _format='{:06x}'):
    """
    Convert int to hex string.

    :param value:
    :param _format:
    :return:
    """
    if not isinstance(value, int):
        raise ValueError('Required int.')
    return _format.format(value)


def hexstr_to_int(value, base=16):
    """
    Convert hex string to int.

    :param value:
    :param base:
    :return:
    """
    return int(value, base=base)


def access_object_member(value, member_name, *args, **kwargs):
    """
    Handle accessing object built-in members (properties and functions).

    :param value:
    :param member_name:
    :param args:
    :param kwargs:
    :return:
    """
    if hasattr(value, member_name):
        member = getattr(value, member_name)
        if callable(member):
            return member(*args, **kwargs)
        return member
    else:
        raise UnsupportedOperation('Unsupported operation for {}: {}'.format(value, member_name))


def validate_3octets(value):
    """
    Validate 3-octets string.

    :param value:
    :return:
    """
    is_valid = False
    try:
        is_valid = int(value, base=16) >= 0 and len(value) == 6
    except ValueError:
        is_valid = False
    except TypeError:
        is_valid = False
    except Exception:
        is_valid = False
    return is_valid


def validate_MAC(value):
    """
    Validate MAC address.

    :param value: EUI-48 MAC address
    :return:
    """
    cleaned = extract_alphanumeric(value)
    is_valid = False
    try:
        is_valid = hexstr_to_int(cleaned) >= 0
    except ValueError:
        is_valid = False
    except TypeError:
        is_valid = False
    except Exception:
        is_valid = False
    return is_valid


class MacGenerator(object):
    """
    Class to generate EUI-48 MAC Addresses.
    """

    pattern_oui = None

    def __init__(self, oui=None, start=None, stop=None, total=1,
        delimiter=':', case='lower'):
        """
        :param oui: 6-digit organizationally unique identifier
        :param start: NIC specific start address
        :param stop: NIC specific end address
        :param total: Total number to generate
        :param delimiter: Delimiter for MAC address
        :param case: Use lower or upper
        """
        self.oui = oui
        self.start = start
        self.i_start = 0  # integer value of "start"
        self.stop = stop
        self.i_stop = 0  # integer value of "stop"
        self.total = total
        self.delimiter = delimiter
        self.case = case

    def normalize_oui(self):
        """
        Normalize OUI by using delimiter.

        :return:
        """
        cleaned = extract_alphanumeric(self.oui)
        return pair_hexvalue(cleaned, delimiter=self.delimiter)

    def __validate(self):
        """
        Validate input values.
        """
        if not self.oui:
            self.oui = int_to_hexstr(random.randint(0, 255))
        else:
            self.oui = extract_alphanumeric(self.oui)
            if not validate_3octets(self.oui):
                raise ValueError('Invalid OUI value.')

        if not self.start:
            self.i_start = random.randint(0, 255)
        else:
            self.start = extract_alphanumeric(self.start)
            if not validate_3octets(self.start):
                raise ValueError('Invalid value for starting address.')
            else:
                self.i_start = hexstr_to_int(self.start)

        if not self.stop:
            is_valid_total = self.total and \
                access_object_member(self.total, 'real') and self.total >= 0
            if not is_valid_total:
                raise ValueError('Invalid value for total.')
            else:
                self.i_stop = self.i_start + self.total
        else:
            if not self.start:
                raise ValueError(
                    'Invalid usage. Use -s along with -r together.')
            self.stop = extract_alphanumeric(self.stop)
            if not validate_3octets(self.stop):
                raise ValueError('Invalid value for ending address.')
            else:
                self.i_stop = hexstr_to_int(self.stop)

    def __build(self):
        """
        Build generator object.

        :return:
        """
        self.oui = self.normalize_oui()
        for each in range(self.i_start, self.i_stop):
            dev_id = pair_hexvalue(int_to_hexstr(each), delimiter=self.delimiter)
            generated_mac = '{oui}{delimiter}{dev}'.format(
                oui=self.oui,
                delimiter=self.delimiter,
                dev=dev_id
            )
            yield access_object_member(generated_mac, self.case)

    def generate(self):
        """
        Generate EUI-48 MAC addresses.
        :return:
        """
        self.__validate()
        return self.__build()


def handle_args():
    parser = argparse.ArgumentParser(
        description='MAC address generator library for testers.')
    parser.add_argument('-o', '--oui',
        help='6-digit organizationally unique identifier')
    parser.add_argument('-r', '--start',
        help='NIC specific start address')
    parser.add_argument('-s', '--stop',
        help='NIC specific end address')
    parser.add_argument('-t', '--total', type=int, default=1,
        help='Number of MACs to generate')
    parser.add_argument('-d', '--delimiter', default=':',
        help='Delimiter for MAC address')
    parser.add_argument('-c', '--case', default='lower',
        help='Use lower or upper')
    return parser.parse_args()


def main():
    try:
        args = vars(handle_args())
        macg = MacGenerator(**args)
        print('\n'.join(list(macg.generate())))
    except Exception as exc:
        print(exc)


if __name__ == '__main__':
    main()
