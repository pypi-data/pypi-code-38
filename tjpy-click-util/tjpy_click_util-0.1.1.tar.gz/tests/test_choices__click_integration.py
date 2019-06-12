from typing import List, Any

import click
from pytest import fixture

import tjpy_click_util.choices \
    as mut
from tjpy_click_util.test_cli_invoke import invoke_cli

mut_name = mut.__name__


def _create_command_with_argument(argument_type: click.ParamType):
    @click.command()
    @click.argument('value', type=argument_type)
    def test_command(value):
        click.echo(f"provided value: {str(value)} of type {type(value)}")

    return test_command


####
# string values

@fixture
def _command_with_string_values():
    class TypeWithStringValues(mut.DynamicChoiceParamType):

        @property
        def _choices(self) -> List[Any]:
            return ["val1", "val2"]

    return _create_command_with_argument(TypeWithStringValues())


class TestStringValues:
    def test_help(self, _command_with_string_values):
        result = invoke_cli(["--help"], _command_with_string_values)

        assert '--help  Show this message and exit.' in result.output
        assert 'val1' in result.output
        assert 'val2' in result.output

    def test_one_value(self, _command_with_string_values):
        result = invoke_cli(["val2"], _command_with_string_values)

        assert f"provided value: val2 of type {str}" in result.output

    def test_wrong_value(self, _command_with_string_values):
        result = invoke_cli(["wrong_value"], _command_with_string_values, verify_successful=False)

        assert result.exit_code == 2

        assert "Invalid value" in result.output
        assert "(choose from val1, val2)" in result.output


####
# custom type with custom string-method for choice

class CustomStringableType:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


@fixture
def _command_with_custom_stringable_type():
    class TypeWithStringableValues(mut.DynamicChoiceParamType):

        @property
        def _choices(self) -> List[Any]:
            return [CustomStringableType("val1"), CustomStringableType("val2")]

    return _create_command_with_argument(TypeWithStringableValues())


class TestCustomTypeForChoice:

    def test_help(self, _command_with_custom_stringable_type):
        result = invoke_cli(["--help"], _command_with_custom_stringable_type)

        assert '--help  Show this message and exit.' in result.output
        assert 'val1' in result.output
        assert 'val2' in result.output

    def test_one_value(self, _command_with_custom_stringable_type):
        result = invoke_cli(["val2"], _command_with_custom_stringable_type)

        assert f"provided value: val2 of type {CustomStringableType}" in result.output

    def test_wrong_value(self, _command_with_custom_stringable_type):
        result = invoke_cli(["wrong_value"], _command_with_custom_stringable_type, verify_successful=False)

        assert result.exit_code == 2

        assert "Invalid value" in result.output
        assert "(choose from val1, val2)" in result.output


####
# custom type without str method but custom string-method for choice


class CustomTypeWithoutStrFunction:
    def __init__(self, value: str):
        self.value = value


@fixture
def _command_with_custom_not_stringable_type():
    class TypeWithCustomChoiceToStrFunction(mut.DynamicChoiceParamType):

        @property
        def _choices(self) -> List[Any]:
            return [CustomTypeWithoutStrFunction("val1"), CustomTypeWithoutStrFunction("val2")]

        def _choice_to_string(self, choice: Any):
            return choice.value

    return _create_command_with_argument(TypeWithCustomChoiceToStrFunction())


class TestCustomChoiceToStrFunction:

    def test_help(self, _command_with_custom_not_stringable_type):
        result = invoke_cli(["--help"], _command_with_custom_not_stringable_type)

        assert '--help  Show this message and exit.' in result.output
        assert 'val1' in result.output
        assert 'val2' in result.output

    def test_one_value(self, _command_with_custom_not_stringable_type):
        result = invoke_cli(["val2"], _command_with_custom_not_stringable_type)

        assert f"of type {CustomTypeWithoutStrFunction}" in result.output

    def test_wrong_value(self, _command_with_custom_not_stringable_type):
        result = invoke_cli(["wrong_value"], _command_with_custom_not_stringable_type, verify_successful=False)

        assert result.exit_code == 2

        assert "Invalid value" in result.output
        assert "(choose from val1, val2)" in result.output


####
# verify options are only resolved when necessary


@fixture
def _command_throwing_exception_if_choice_argument_options_resolved():
    class TypeWhichNeverShouldBeResolved(mut.DynamicChoiceParamType):

        @property
        def _choices(self) -> List[Any]:
            raise Exception("choices have been resolved")

    return _create_command_with_argument(TypeWhichNeverShouldBeResolved())


class TestNotInvokedUntilNeeded:

    def test_help(self, _command_throwing_exception_if_choice_argument_options_resolved):
        try:
            invoke_cli(["--help"], _command_throwing_exception_if_choice_argument_options_resolved)
        except Exception as exception:
            assert 'choices have been resolved' in exception.args[0]
        else:
            raise Exception("should have thrown exception")

    def test_definition_only_is_fine(self, _command_throwing_exception_if_choice_argument_options_resolved):
        # coming here means that it has not resolved the values immediately
        pass
