import json, pytz
from datetime import datetime

BOOLEAN_TRUE_VALUES = [True, 1, "true", "t", "yes", "y", "1"]
BOOLEAN_FALSE_VALUES = [False, 0, "false", "f", "no", "n", "0"]
BOOLEAN_VALUES = BOOLEAN_TRUE_VALUES + BOOLEAN_FALSE_VALUES

def is_truthy(value):
  return not is_falsey(value)

def is_falsey(value):
  """ Falsey values - None, False, "False", "No", 0, "" """
  if value == None or value == False or value == 0:
    return True
  value_string = str(value).lower()
  return len(value_string) == 0 or value_string in BOOLEAN_FALSE_VALUES

def parse_date_from(input_date, format=None):
  if input_date:
    if isinstance(input_date, datetime):
      return input_date
    else:
      for fmt in [format, "%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d-%H-%M", "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%f%z"]:
        try:
          parsed_date = datetime.strptime(input_date, fmt)
          return parsed_date if parsed_date.tzinfo else parsed_date.replace(tzinfo=pytz.UTC)
        except:
          pass
  return None

def is_different(key, from_value, to_value):
  if from_value == None and to_value == None:
    return False
  if (from_value != None and to_value == None) or (to_value != None and from_value == None):
    return True
  if is_boolean(from_value):
    return convert_to_boolean(from_value) != convert_to_boolean(to_value)
  if isinstance(from_value, str) and isinstance(to_value, str):
    # for strings type, let it be CASE INSENSITIVE
    return from_value.lower().strip() != to_value.lower().strip()
  # TODO date support. leaving for now

  return from_value != to_value

def is_boolean(value):
  if value in (BOOLEAN_VALUES) or str(value).lower() in (BOOLEAN_VALUES):
    return True
  else:
    return False

def convert_to_boolean(value):
  if value in BOOLEAN_TRUE_VALUES or str(value).lower() in BOOLEAN_TRUE_VALUES:
    return True
  elif value in BOOLEAN_FALSE_VALUES or str(value).lower() in BOOLEAN_FALSE_VALUES:
    return False
  else:
    return None
