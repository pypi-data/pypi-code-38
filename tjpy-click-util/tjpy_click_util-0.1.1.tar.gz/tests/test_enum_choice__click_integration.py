from enum import Enum

import click
from pytest import fixture

import tjpy_click_util.enum_choice \
    as mut
from tjpy_click_util.test_cli_invoke import invoke_cli

mut_name = mut.__name__


def _create_command_with_argument(argument_type: click.ParamType):
    @click.command()
    @click.argument('value', type=argument_type)
    def test_command(value):
        click.echo(f"provided value: {str(value)} of type {type(value)}")

    return test_command


class _MyTestEnum(Enum):
    val1 = 1,
    val2 = 2,
    val3 = 3


@fixture
def _command_with_enum_param():
    my_enum_param_type = mut.EnumChoiceParamType(_MyTestEnum)
    return _create_command_with_argument(my_enum_param_type)


def test_help(_command_with_enum_param):
    result = invoke_cli(["--help"], _command_with_enum_param)

    assert '--help  Show this message and exit.' in result.output
    assert 'val1' in result.output
    assert 'val2' in result.output


def test_one_value(_command_with_enum_param):
    result = invoke_cli(["val2"], _command_with_enum_param)

    assert f"provided value: _MyTestEnum.val2 of type {_MyTestEnum}" in result.output
