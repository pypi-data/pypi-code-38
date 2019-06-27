import json
import warnings

from orchestrate.common import safe_format


def show_overwrite_warning(warning_for, value):
  warnings.warn(safe_format(
    "The log for {warning_for} has been overwritten. Previous value: {value}",
    warning_for=warning_for,
    value=value,
  ), RuntimeWarning)

class LogParser(object):
  def __init__(self, path, metrics):
    self.metric_names = [metric['name'] for metric in metrics]
    self.values = {}
    self.metadata = {}
    self.failed = False
    self.unknown_parameters = {}
    log_type_handlers = {
      'failed': self.set_failed,
      'metric': self.set_metric,
      'metadata': self.set_metadata,
      'unknown_parameter': self.set_unknown_parameter,
    }
    with open(path) as log_fp:
      for line in log_fp:
        line_json = json.loads(line)
        log_type, data = line_json['type'], line_json['data']
        handler = log_type_handlers[log_type]
        if handler:
          handler(**data)

  def set_metric(self, name, value, value_stddev=None):
    try:
      old_value = self.values[name]
      show_overwrite_warning(safe_format("the metric {}", repr(name)), old_value)
    except KeyError:
      pass
    self.values[name] = {'name': name, 'value': value, 'value_stddev': value_stddev}

  def set_metadata(self, key, value):
    try:
      old_value = self.metadata[key]
      show_overwrite_warning(safe_format("metadata key {}", repr(key)), old_value)
    except KeyError:
      pass
    self.metadata[key] = value

  def set_failed(self):
    self.failed = True

  def set_unknown_parameter(self, name, default):
    self.unknown_parameters[name] = default

  def get_observation_data(self):
    metric_names = self.metric_names
    failed = self.failed

    if failed:
      missing_metrics = []
    else:
      missing_metrics = [metric_name for metric_name in metric_names if metric_name not in self.values]
      if missing_metrics:
        failed = True

    if failed:
      metric_names = []

    value_list = [self.values[metric_name] for metric_name in metric_names]

    def to_meta(value_log):
      name = value_log['name']
      if name in metric_names:
        return
      yield name, value_log['value']
      stddev = value_log.get('value_stddev')
      if stddev is not None:
        yield safe_format('{}_stddev', name), stddev

    metadata = self.metadata.copy()
    metadata.update(self.unknown_parameters)
    metadata.update(
      pair for value_log in self.values.values()
      for pair in to_meta(value_log)
    )

    return value_list, metadata, failed, missing_metrics
