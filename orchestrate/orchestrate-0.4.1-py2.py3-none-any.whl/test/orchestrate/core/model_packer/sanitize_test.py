import pytest

from orchestrate.core.model_packer.service import sanitize_command, sanitize_command_str_or_list


class TestSanitizeCommands(object):
  @pytest.mark.parametrize('command,expected', [
    ('cmd', 'cmd'),
    ('bash -c "python"', 'bash -c "python"'),
    (True, 'True'),
    (False, 'False'),
    (None, ''),
  ])
  def test_sanitize_command(self, command, expected):
    assert sanitize_command(command) == expected

  @pytest.mark.parametrize('commands,expected', [
    (['echo hello'], ['echo hello']),
    ('echo', ['echo']),
    ('bash -c "python"', ['bash -c "python"']),
    ([None, 'pip install -r requirements.txt'], ['', 'pip install -r requirements.txt']),
    (['echo hello', True, False], ['echo hello', 'True', 'False']),
    (123, ['123']),
    (None, []),
  ])
  def test_sanitize_command_str_or_list(self, commands, expected):
    assert sanitize_command_str_or_list(commands) == expected
