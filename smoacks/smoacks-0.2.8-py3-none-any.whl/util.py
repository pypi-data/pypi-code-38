# util.py - Utility functions that are used in multople places
import re

# This code came from a StackOverflow answer
# https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase/19053800
def to_camelcase(value):
    components = value.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])

def to_mixedcase(value):
    components = value.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)

# This code came from a StackOverflow answer
# https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
def to_snakecase(value):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()