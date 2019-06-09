import sys
from .pull_check import pull_check

def api_pull(files_compose):
  pull_check_result = pull_check(files_compose, verbose=True)
  if(pull_check_result['error']):
    sys.exit(1)