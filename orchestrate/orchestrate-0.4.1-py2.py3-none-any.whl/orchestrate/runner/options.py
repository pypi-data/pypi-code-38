import json
import os


class Options(object):
  def __init__(self, config_path, log_path, suggestion_path, pod_name, experiment_id):
    self.config_path = config_path
    self.log_path = log_path
    self.suggestion_path = suggestion_path
    self.pod_name = pod_name
    self.experiment_id = experiment_id

  @classmethod
  def from_env(cls):
    return cls(
      config_path=os.environ.get('ORCHESTRATE_CONFIG', '/etc/orchestrate/config.json'),
      log_path=os.environ.get('ORCHESTRATE_LOG', '/var/orchestrate/log.json'),
      suggestion_path=os.environ.get('ORCHESTRATE_SUGGESTION', '/var/orchestrate/suggestion.json'),
      pod_name=os.environ.get('POD_NAME', 'unknown'),
      experiment_id=os.environ['ORCHESTRATE_EXPERIMENT_ID'],
    )

  def load_config(self):
    with open(self.config_path) as config_fp:
      return json.load(config_fp)
