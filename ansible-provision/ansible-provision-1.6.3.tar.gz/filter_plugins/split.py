from ansible import errors

import re

def split_string(string, separator=' '):
    return string.split(separator)

def split_regex(string, separator_pattern='\s+'):
    return re.split(separator_pattern, string)

class FilterModule(object):
    ''' A filter to split a string into a list. '''
    def filters(self):
        return {
            'split' : split_string,
            'split_regex' : split_regex,
        }