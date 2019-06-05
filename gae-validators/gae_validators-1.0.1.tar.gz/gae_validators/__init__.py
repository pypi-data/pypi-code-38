from datetime import datetime
import re

# python 3 support
PY3 = False
try:
    unicode('')
except NameError:
    PY3 = True
    unicode = str

ONE_MB = 2 ** 20
INT_SIZE = 2 ** 63 # 63 bits plus 1 bit for sign = 64 bit signed integer
EMAIL_USER = re.compile(r"^[^ \t\n\r@<>()]+$", re.I)
EMAIL_DOMAIN = re.compile(r'''
    ^(?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # subdomain
    [a-z]{2,}$                       # TLD
''', re.I | re.VERBOSE)

# based on Django's but with limited schemes: https://github.com/django/django/blob/master/django/core/validators.py
URL = re.compile(
    r'^(?:http|https)://' # scheme
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|' # domain
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)


def validateString(source, max_length=500, newlines=False, encoding='utf-8'):

    valid = True
    if source is None:
        value = ''
    elif PY3:
        if isinstance(source, bytes):
            try:
                value = source.decode(encoding)
            except UnicodeDecodeError:
                value = ''
                valid = False
        else:
            value = str(source)
            try:
                value.encode(encoding)
            except UnicodeEncodeError:
                value = ''
                valid = False
    else:
        if isinstance(source, unicode):
            value = source
            try:
                source.encode(encoding)
            except UnicodeEncodeError:
                value = ''
                valid = False
        else:
            try:
                value = unicode(source, encoding)
            except UnicodeDecodeError:
                value = ''
                valid = False

    if valid:
        value = value.strip()

        if len(value) > max_length:
            valid = False
        elif not newlines and ('\n' in value or '\r' in value):
            valid = False

    return valid, value


def validateRequiredString(source, max_length=500, newlines=False, encoding='utf-8'):

    valid, value = validateString(source, max_length=max_length, newlines=newlines, encoding=encoding)

    if valid and not value:
        valid = False

    return valid, value


def validateText(source, max_length=ONE_MB, newlines=True, encoding='utf-8'):

    return validateString(source, max_length=max_length, newlines=newlines, encoding=encoding)


def validateRequiredText(source, max_length=ONE_MB, newlines=True, encoding='utf-8'):

    return validateRequiredString(source, max_length=max_length, newlines=newlines, encoding=encoding)


def validateEmail(source):

    valid, value = validateString(source)

    if valid and value:
        parts = value.split('@')
        if len(parts) != 2:
            valid = False
        else:
            username, domain = parts

            if not EMAIL_USER.search(username) or not EMAIL_DOMAIN.search(domain):
                valid = False

    return valid, value


def validateRequiredEmail(source):

    valid, value = validateEmail(source)

    if valid and not value:
        valid = False

    return valid, value


def validatePhone(source):

    valid, value = validateString(source)

    if valid and value:
        digits = [char for char in value if char.isdigit()]
        length = len(digits)
        if length < 10 or length > 15:
            valid = False
        else:
            if length == 10:
                # assume US/Canada with the country code missing
                digits = ['1'] + digits
            value = '+' + ''.join(digits)

    return valid, value


def validateRequiredPhone(source):

    valid, value = validatePhone(source)

    if valid and not value:
        valid = False

    return valid, value


def validateUrl(source):

    valid, value = validateString(source)

    if valid and value:
        if '//' not in value:
            value = 'http://' + value

        if not URL.search(value):
            valid = False

    return valid, value


def validateRequiredUrl(source):

    valid, value = validateUrl(source)

    if valid and not value:
        valid = False

    return valid, value


def validateChoices(source, choices):

    valid, value = validateString(source)

    if valid and value:
        valid = value in choices

    return valid, value


def validateRequiredChoices(source, choices):

    valid, value = validateChoices(source, choices)

    if valid and not value:
        valid = False

    return valid, value


def validateBool(source):

    valid = True
    # this can't throw an exception as all types have a boolean value, so no need to wrap it in a try
    value = bool(source)

    return valid, value


def validateInt(source, min_amount=-INT_SIZE, max_amount=INT_SIZE - 1):
    # one is subtracted from the max amount because 0 counts as a possible value on the positive side

    valid = True
    if source:
        try:
            value = int(source)
        except ValueError:
            value = None
            valid = False

        if valid and (min_amount > value or max_amount < value):
            valid = False
    else:
        value = None

    return valid, value


def validateRequiredInt(source, min_amount=-INT_SIZE, max_amount=INT_SIZE - 1):

    valid, value = validateInt(source, min_amount=min_amount, max_amount=max_amount)

    if valid and not value:
        valid = False

    return valid, value


def validateFloat(source, min_amount=-INT_SIZE, max_amount=INT_SIZE - 1):

    valid = True
    if source:
        try:
            value = float(source)
        except ValueError:
            value = None
            valid = False

        if valid and (min_amount > value or max_amount < value):
            valid = False
    else:
        value = None

    return valid, value


def validateRequiredFloat(source, min_amount=-INT_SIZE, max_amount=INT_SIZE - 1):

    valid, value = validateFloat(source, min_amount=min_amount, max_amount=max_amount)

    if valid and not value:
        valid = False

    return valid, value


def validateDateTime(source, date_format="%Y-%m-%dT%H:%M", future_only=False, past_only=False):
    # note that this is not aware of timezones
    # recommend ISO format for sending from JS or other non-user sources: "%Y-%m-%dT%H:%M:%S.%fZ"
    assert not future_only or not past_only, "There are no dates in both the future and the past."

    valid = True
    if source:
        try:
            value = datetime.strptime(source, date_format)
        except ValueError:
            value = None
            valid = False

        if valid:
            if future_only and value < datetime.utcnow():
                valid = False
            elif past_only and value > datetime.utcnow():
                valid = False
    else:
        value = None

    return valid, value


def validateRequiredDateTime(source, date_format="%Y-%m-%dT%H:%M", future_only=False, past_only=False):

    valid, value = validateDateTime(source, date_format=date_format, future_only=future_only, past_only=past_only)

    if valid and not value:
        valid = False

    return valid, value


def validateDate(source, date_format="%Y-%m-%d", future_only=False, past_only=False):

    valid, value = validateDateTime(source, date_format=date_format, future_only=future_only, past_only=past_only)

    if value:
        value = value.date()

    return valid, value


def validateRequiredDate(source, date_format="%Y-%m-%d", future_only=False, past_only=False):

    valid, value = validateDate(source, date_format=date_format, future_only=future_only, past_only=past_only)

    if valid and not value:
        valid = False

    return valid, value


def validateTime(source, time_format="%H:%M"):

    valid, value = validateDateTime(source, date_format=time_format)

    if value:
        value = value.time()

    return valid, value


def validateRequiredTime(source, time_format="%H:%M"):

    valid, value = validateTime(source, time_format=time_format)

    if valid and not value:
        valid = False

    return valid, value
