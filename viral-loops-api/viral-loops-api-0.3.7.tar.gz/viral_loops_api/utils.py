from .exceptions import InvalidChoiceException


def validate_enum(value, possible):
  """
  Throws an exception if a given value is outside the list of possible values.
  Returns the value if it is a valid choice.
  """
  if value not in possible:
    raise InvalidChoiceException(f'{value} not in {possible}')

  return value
