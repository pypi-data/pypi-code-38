from ansible import errors

import re

def find_subnets(all_subnets, name, az=''):
    _list = []

    for subnet in all_subnets:
        if subnet['tags'].get('Name', '').startswith(name) and (az == '' or subnet["availability_zone"] == az):
                _list.append(subnet)
    return _list

class FilterModule(object):
    ''' A filter to split a string into a list. '''
    def filters(self):
        return {
            'find_subnets' : find_subnets
        }