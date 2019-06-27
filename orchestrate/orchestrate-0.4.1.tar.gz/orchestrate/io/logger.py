import json
import math
import sys

import six

from orchestrate.common import safe_format


def validate_name(warn, name):
  if not isinstance(name, six.string_types):
    raise ValueError(safe_format(
      "The {} must be a string, not {}",
      warn,
      type(name).__name__
    ))

def sanitize_number(warn, name, value):
  if isinstance(value, six.integer_types):
    return value
  else:
    try:
      value = float(value)
      if math.isinf(value) or math.isnan(value):
        raise ValueError(safe_format("`{}` is not an appropriate number", value))
      else:
        return value
    except (ValueError, TypeError) as err:
      six.raise_from(ValueError(safe_format(
        "The {} logged for `{}` could not be converted to a number: {}",
        warn,
        name,
        repr(value),
      )), err)

class Logger(object):
  def __init__(self, config):
    self.config = config

  def write_log(self, log_type, data):
    payload = {'type': log_type, 'data': data}

    def dump(fp):
      json.dump(payload, fp)
      fp.write('\n')

    if self.config.is_enabled:
      with open(self.config.log_location, 'a') as log_fp:
        dump(log_fp)
    else:
      dump(sys.stdout)
      sys.stdout.flush()

  def log_metric(self, name, value, stddev=None):
    validate_name('metric name', name)
    metric_log = {'name': name}
    metric_log['value'] = sanitize_number('metric', name, value)
    if stddev is not None:
      metric_log['value_stddev'] = sanitize_number('metric stddev', name, stddev)
    self.write_log('metric', metric_log)

  def log_metadata(self, key, value):
    validate_name('metadata key', key)
    if not isinstance(value, six.string_types):
      try:
        value = sanitize_number('metadata', key, value)
      except ValueError:
        value = repr(value)
    self.write_log('metadata', {
      'key': key,
      'value': value,
    })

  def log_failure(self):
    self.write_log('failed', {})
