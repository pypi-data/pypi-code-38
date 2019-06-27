from os import environ as _environ

from orchestrate.io.config import Config as _Config
from orchestrate.io.read_suggestion import (
  assignment_getter as _assignment_getter,
  read_suggestion as _read_suggestion,
)
from orchestrate.io.logger import Logger as _Logger

_global_config = _Config(
  is_enabled=_environ.get('ORCHESTRATE_IO_ENABLED') is not None,
  suggestion_location=_environ.get('ORCHESTRATE_SUGGESTION', '/var/orchestrate/suggestion.json'),
  log_location=_environ.get('ORCHESTRATE_LOG', '/var/orchestrate/log.json'),
)

_global_logger = _Logger(_global_config)
log_metric = _global_logger.log_metric
log_metadata = _global_logger.log_metadata
log_failure = _global_logger.log_failure

suggestion = _read_suggestion(_global_config)
assignment = _assignment_getter(_global_config, _global_logger, suggestion)
task = suggestion.task
