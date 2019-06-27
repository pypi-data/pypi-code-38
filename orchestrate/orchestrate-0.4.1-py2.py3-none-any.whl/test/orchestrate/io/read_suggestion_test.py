from test.orchestrate.io.test_base import IoTestBase

import pytest

from orchestrate.io.read_suggestion import assignment_getter, read_suggestion


class TestReadSuggestion(IoTestBase):
  def test_read_suggestion_with_io_enabled(
    self,
    enabled_config,
    logger_io_enabled,
    fake_suggestion,
  ):
    suggestion = read_suggestion(enabled_config)
    assert suggestion.id == fake_suggestion['id']
    assert suggestion.assignments['first_param'] == fake_suggestion['assignments']['first_param']
    assert suggestion.to_json() == fake_suggestion
    getter = assignment_getter(enabled_config, logger_io_enabled, suggestion)
    default = object()
    assert getter('first_param', default) is not default
    assert getter('first_param', default) == fake_suggestion['assignments']['first_param']

  def test_warn_unknown_param_with_io_enabled(
    self,
    enabled_config,
    logger_io_enabled,
    fake_suggestion,
  ):
    suggestion = read_suggestion(enabled_config)
    getter = assignment_getter(enabled_config, logger_io_enabled, suggestion)
    default = 'default_value'
    with pytest.warns(RuntimeWarning):
      assert getter('unknown_param', default=default) is default

  def test_read_suggestion_with_io_disabled(self, disabled_config, logger_io_disabled):
    suggestion = read_suggestion(disabled_config)
    assert suggestion.id is None
    assert suggestion.assignments.to_json() == {}
    getter = assignment_getter(disabled_config, logger_io_disabled, suggestion)
    default = object()
    assert getter('first_param', default) is default
