import sys
import yaml
import traceback
from .printError import printError

def parse_yaml(file):
  with open(file) as yamlfile:
    try:
      parsed = yaml.safe_load(yamlfile.read())
    except yaml.YAMLError as exc:
      if hasattr(exc, 'problem_mark'):
        mark = exc.problem_mark
        printError("YAML Syntax Error file: %s at line: %s, col: %s" % (file, mark.line+1, mark.column+1))
      printError(traceback.format_exc())
      sys.exit(1)
  return parsed