import string
import pytest

import pyssword as m

# Run:
# $ pytest -rapP test_pyssword.py


def test_run_help(cli_invoker):
    result = cli_invoker(m.main, 'run -h'.split())
    assert result.exit_code == 0
    assert result.output.startswith('Usage: main run <options> <size>')


@pytest.mark.parametrize(
    'size', [
        *[pytest.param(i, marks=pytest.mark.xfail) for i in range(0, 10)],
        *range(10, 21),
    ]
)
def test_run_size(cli_invoker, size):
    result = cli_invoker(m.main, f'run {size}'.split())
    assert result.exit_code == 0
    assert len(result.output.strip()) == size


def test_run_full_punctuation(cli_invoker):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    result = cli_invoker(m.main, 'run'.split())
    output = result.output.strip()

    assert result.exit_code == 0
    assert len(output) == 16
    assert not any(c not in alphabet for c in output), f"Invalid punctuations --> {tuple(c for c in output if c not in alphabet)} in {output}"


def test_run_small_punctuation(cli_invoker):
    alphabet = string.ascii_letters + string.digits + '!?@#$%&*+-_.,'
    result = cli_invoker(m.main, 'run -s'.split())
    output = result.output.strip()

    assert result.exit_code == 0
    assert len(output) == 16
    assert not any(c not in alphabet for c in output), f"Invalid punctuations --> {tuple(c for c in output if c not in alphabet)} in {output}"


def test_run_nopunctuation(cli_invoker):
    alphabet = string.ascii_letters + string.digits
    result = cli_invoker(m.main, 'run -n'.split())
    output = result.output.strip()

    assert result.exit_code == 0
    assert len(output) == 16
    assert not any(c not in alphabet for c in output), f"Invalid punctuations {tuple(c for c in output if c not in alphabet)} in {output}"


def test_run_small_and_nopunctuation(cli_invoker):
    alphabet = string.ascii_letters + string.digits
    result = cli_invoker(m.main, 'run -n -s'.split())
    output = result.output.strip()

    assert result.exit_code == 0
    assert len(output) == 16
    assert not any(c not in alphabet for c in output), f"Invalid punctuations {tuple(c for c in output if c not in alphabet)} in {output}"
