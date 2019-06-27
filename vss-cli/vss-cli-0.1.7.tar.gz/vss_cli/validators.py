import re
import click
import json
import logging

_LOGGING = logging.getLogger(__name__)


def validate_phone_number(ctx, param, phone):
    phone_regex = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|' \
                  r'\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d' \
                  r'{3}[-\.\s]??\d{4})+'
    if not re.match(phone_regex, phone):
        raise click.BadParameter(
            'Value must be in the '
            'following format 416-166-6666'
        )
    return phone


def validate_email(ctx, param, email):
    email_regex = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+' \
                  r'\.[a-zA-Z0-9-.]+$)'
    if not re.match(email_regex, email):
        raise click.BadParameter(
            'Value must be in the '
            'following format user@utoronto.ca'
        )
    return email


def validate_json_type(ctx, param, value):
    try:
        if value is not None:
            return json.loads(value)
    except ValueError as ex:
        _LOGGING.error(f'{ex}')
        raise click.BadParameter(
            f'{param.name} should be a JSON parameter input.'
        )


def validate_admin(ctx, param, value):
    if value:
        _value = value.split(':')
        if not value or len(_value) < 2:
            raise click.BadParameter(
                'Admin should be in the '
                'following format: '
                'FullName:Phone:email'
            )
        validate_email(ctx, param, _value[2])
        validate_phone_number(ctx, param, _value[1])
        return value


def validate_inform(ctx, param, value):
    if value:
        _value = value.split(',')
        if not value:
            raise click.BadParameter(
                'Informational contacts format:'
                'email@utoronto.ca,email2@utoronto.ca'
            )
        for email in _value:
            validate_email(ctx, param, email)
        return value
