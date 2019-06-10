import datetime
import ipaddress
import re
import json
import jsonschema


def required(message="Field is not presented"):
    def check(field: str, dict_to_check: dict):
        if field in dict_to_check:
            return True, None
        else:
            return False, message
    return check


def is_type(type_object, message="Type doesn't is type field"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        if value and isinstance(value, type_object):
            return True, None
        else:
            return False, message
    return check


def str_to_datetime(format_str: str, message="Can convert to date format"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        try:
            dt = datetime.datetime.strptime(value, format_str)
            if isinstance(dt, datetime.datetime):
                return True, None
        except ValueError:
            return False, message
    return check


def min_value(min_val, message="Value is less"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        if value < min_val:
            return True, None
        else:
            return False, message
    return check


def max_value(max_val, message="Value is bigger"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        if value < max_val:
            return True, None
        else:
            return False, message
    return check


def in_list(target_list, message="Value not in list"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        if value in target_list:
            return True, None
        else:
            return False, message
    return check


def list_in_list(target_list, message="Value: '{}' not in target list"):
    def check(field: str, dict_to_check: dict):
        flag = True
        error_value = []
        values = dict_to_check.get(field)
        if not values:
            return True, None
        for value in values:
            if value not in target_list:
                flag = False
                error_value.append(message.format(value))

        if flag:
            return True, None
        else:
            return False, error_value
    return check


def is_ip(message="Value is not ipv4 address"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        try:
            ipaddress.ip_address(value)
            return True, None
        except ValueError:
            return False, message
    return check


def is_email(message="Is not email address"):
    def check(field: str, dict_to_check: dict):
        email_reg = r'[^@]+@[^@]+\.[^@]+'
        value = dict_to_check.get(field)
        if not value:
            return True, None
        if re.match(email_reg, value):
            return True, None
        else:
            return False, message
    return check


def is_phone(message="Is not phone"):
    def check(field: str, dict_to_check: dict):

        phone_reg = r"""([0-9]{10})|([0-9]{3}[-]{1}[0-9]{3}[-]{1}[0-9]{4})|([0-9]{3}[.]{1}[0-9]{3}[.]
        {1}[0-9]{4})|([\(]{1}[0-9]{3}[\)][ ]{1}[0-9]{3}[-]{1}[0-9]{4})|([0-9]{3}[-]{1}[0-9]{4})"""
        value = dict_to_check.get(field)
        if value.count('+') > 1:
            return False, message
        if value.startswith('+'):
            value = value.replace('+', '')
        if not value:
            return True, None
        if re.match(phone_reg, value):
            return True, None
        else:
            return False, message
    return check


def is_url(message="Value is not url"):
    def check(field: str, dict_to_check: dict):

        url_reg = re.compile(r'^(?:http|ftp)s?://' # http:// or https://
                               # domain
                               r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                               #localhost...
                               r'localhost|'
                               r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                               # r'(?::\d+)?' # optional port
                               r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        value = dict_to_check.get(field)

        if not value:
            return True, None
        if re.match(url_reg, value):
            return True, None
        else:
            return False, message
    return check
    pass


def is_numeric(message="Is not numeric"):
    def check(field: str, dict_to_check: dict):
        value = dict_to_check.get(field)
        if not value:
            return True, None
        try:
            float(value)
            return True, None
        except ValueError:
            return False, message
    return check


def regex(reg='', message="Value is correct y regex "):
    def check(field: str, dict_to_check: dict):

        reg_rule = re.compile(reg)

        value = dict_to_check.get(field)

        if not value:
            return True, None
        if re.match(reg_rule, value):
            return True, None
        else:
            return False, message
    return check


def by_json_schema(schema_path, message="Validation schema error"):
    def check(field: str, dict_to_check: dict):
        try:
            with open(schema_path, 'r') as file:
                schema = json.loads(file.read())
                body = dict_to_check.get(field)
                if not body:
                    return True, None

                jsonschema.validate(body, schema)
                return True, None
        except json.decoder.JSONDecodeError as e:
            return False, "JSONDecodeError: {0}".format(e)
        except jsonschema.ValidationError:
            return False, message
        except FileNotFoundError as e:
            return False, "File schema not found: {0}".format(e)
    return check
