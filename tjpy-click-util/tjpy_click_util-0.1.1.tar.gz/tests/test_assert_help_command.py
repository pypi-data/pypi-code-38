import tjpy_click_util.assert_help_command \
    as mut

mut_name = mut.__name__

_some_simple_help_output = """Usage: config show missing [OPTIONS]

  Show missing configuration.

Options:
  --help  Show this message and exit.
"""

_some_complex_help_output = """Usage: playbooks install [OPTIONS] PLAYBOOK [R6ADMIN|ROOT]
                         [ADDITIONAL_ARGUMENT]...

  Invoke install.sh for playbook and given parameters

Options:
  -x, --environment [btv8/dev-01|test_project/dev-01]
  --help                          Show this message and exit.
"""


def test_simple__success():
    mut.assert_help_command_usage_syntax(
        _some_simple_help_output,
        "config show missing [OPTIONS]")


def test_simple__failure():
    try:
        mut.assert_help_command_usage_syntax(
            _some_simple_help_output,
            "config show missing")
    except AssertionError:
        pass
    else:
        raise Exception("Should have thrown exception")


def test_complex__success():
    mut.assert_help_command_usage_syntax(
        _some_complex_help_output,
        "playbooks install [OPTIONS] PLAYBOOK [R6ADMIN|ROOT] [ADDITIONAL_ARGUMENT]...")


def test_complex__failure():
    try:
        mut.assert_help_command_usage_syntax(
            _some_complex_help_output,
            "playbooks install [OPTIONS] PLAYBOOK [R6ADMIN|ROOT] [NOPE_ARGUMENT]...")
    except AssertionError:
        pass
    else:
        raise Exception("Should have thrown exception")
