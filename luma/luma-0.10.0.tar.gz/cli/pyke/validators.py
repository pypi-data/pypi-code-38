import click

def validate_str_literal(type, value):
    if isinstance(type, list):
        return validate_list(value)

def validate_list(value):
    if value[0] != "[" and value[1] != "'"\
    and value[-2] != "'" and value[-1] != "]":
        raise click.BadParameter(css_includes)
