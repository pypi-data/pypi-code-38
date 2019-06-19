
from .constants import VALID_RECIPE

def is_valid_recipe_dict(to_test):
    """Validates that the passed dictionary expresses a recipe"""

    if not to_test:
        return (False, 'A workflow recipe was not provided')

    if not isinstance(to_test, dict):
        return (False, 'The workflow recipe was incorrectly formatted')

    message = 'The workflow recipe had an incorrect structure'
    for key, value in to_test.items():
        if key not in VALID_RECIPE:
            message += ' Is missing key %s' % key
            return (False, message)
        if not isinstance(value, VALID_RECIPE[key]):
            message += ' %s is expected to have type %s but actually has %s' \
                       % (value, VALID_RECIPE[key], type(value))
            return (False, message)
    return (True, '')