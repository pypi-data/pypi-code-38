from . import utils


def test_locate_command():
    result = utils.locate_command("bash")
    assert result.returncode == 0
    assert result.output == "/bin/bash"

    result = utils.locate_command("this_is_not_a_real_command")
    assert result.returncode == 1
