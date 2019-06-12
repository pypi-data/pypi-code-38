import re


def assert_help_command_usage_syntax(output: str, expected_syntax: str):
    assert output.startswith("Usage: ")
    syntax_and_description_split_line_position = output.find("\n\n")
    usage_output = output[:syntax_and_description_split_line_position]
    usage_output = usage_output.replace("\n", " ")
    usage_output = re.sub("[ ]{2,}", " ", usage_output)
    usage_output = usage_output.replace("Usage: ", "")
    assert usage_output == expected_syntax
