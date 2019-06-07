# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
def parse_data(data):
    if isinstance(data, str):
        if not data: # empty string, i.e., ''
            return [ ]
        return [data]
    return data

##__________________________________________________________________||
