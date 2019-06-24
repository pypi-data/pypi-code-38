import re


def convert_to_enumeration_value(value: str, value_if_blank='unknown') -> str:
    """
    Converts a value to the common formatting for an enumeration_value:

    1. all characters are converted to lowercase
    2. all numbers, letters, and underscores are kept
    3. all other characters are replaced by underscores
    4. extra underscores are removed from the ends
    5. continuous runs of underscore characters are shortened to "_"

    `"_1 - Some Value - w/ Formatting..."` -> `"1_some_value_w_formatting"`
    """
    value = value.lower()
    value = re.sub(r'[^\w]+', '_', value)
    value = value.strip(' _')
    value = re.sub(r'_+', '_', value)
    return value or value_if_blank
