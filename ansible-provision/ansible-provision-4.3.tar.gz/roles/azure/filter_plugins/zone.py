import re

def zone(hostname,count=2):
    i = int(re.findall('\d+$', hostname)[0])
    if i == 1:
        return 1
    elif i == 2:
        return 2
    elif i == 3:
        return 1
    elif i == 4:
        return 2


class FilterModule(object):
     def filters(self):
         return {'zone': zone}

if __name__ == '__main__':
    assert zone("AB8C01") == 1
    assert zone("ABC01") == 1
    assert zone("ABC02") == 2
    assert zone("ABC03") == 1
    assert zone("ABC01",2) == 1
    assert zone("ABC02",2) == 2
    assert zone("ABC03",2) == 1
