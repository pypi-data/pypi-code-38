import json
import os

from orchestrate.runner.options import Options


def test_open_log_file(options):
  open(options.log_path, 'w').close()

def test_open_suggestion_file(options):
  open(options.suggestion_path, 'w').close()

def test_load_config(options):
  with open(options.config_path, 'w') as config_fp:
    json.dump({'metrics': [], 'parameters': []}, config_fp)
  options.load_config()

if __name__ == '__main__':
  os.environ['ORCHESTRATE_EXPERIMENT_ID'] = '42'
  os.environ['POD_NAME'] = 'test pod'
  options = Options.from_env()
  assert options.experiment_id == '42', options.experiment_id
  assert options.pod_name == 'test pod', options.pod_name
  for test in (
    test_open_log_file,
    test_open_suggestion_file,
    test_load_config,
  ):
    test(options)
