import json
import tempfile

import pytest

from orchestrate.io.config import Config
from orchestrate.io.logger import Logger


class IoTestBase(object):
  @pytest.fixture
  def fake_suggestion(self):
    return {'assignments': {'first_param': 1}, 'id': '42'}

  @pytest.fixture
  def suggestion_path(self, fake_suggestion):
    with tempfile.NamedTemporaryFile('w') as suggestion_fp:
      json.dump(fake_suggestion, suggestion_fp)
      suggestion_fp.flush()
      yield suggestion_fp.name

  @pytest.fixture
  def log_path(self):
    with tempfile.NamedTemporaryFile() as log_fp:
      yield log_fp.name

  @pytest.fixture
  def enabled_config(self, suggestion_path, log_path):
    return Config(
      is_enabled=True,
      suggestion_location=suggestion_path,
      log_location=log_path,
    )

  @pytest.fixture
  def disabled_config(self):
    return Config(
      is_enabled=False,
      suggestion_location=None,
      log_location=None,
    )

  @pytest.fixture
  def logger_io_enabled(self, enabled_config):
    return Logger(enabled_config)

  @pytest.fixture
  def logger_io_disabled(self, disabled_config):
    return Logger(disabled_config)
