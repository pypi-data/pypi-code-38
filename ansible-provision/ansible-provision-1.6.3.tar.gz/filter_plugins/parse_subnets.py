def parse_subnets(all_subnets):
    _list = {}

    for subnet in all_subnets:
        if subnet['tags']['Name'] not in _list:
            _list[subnet['tags']['Name']] = {}
        _list[subnet['tags']['Name']][subnet['availability_zone']] = subnet['id']
    return _list

class FilterModule(object):
    ''' A filter to split a string into a list. '''
    def filters(self):
        return {
            'parse_subnets' : parse_subnets
        }