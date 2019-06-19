import re

def zone(hostname,count=3,region=""):
    i = int(re.findall('\d+$', hostname)[0]) % count
    if region == "ap-northeast-2":
        return "a" if i % 2 == 1 else "c"
    if count == 1 or i == 1:
        return 'a'
    if i == 0:
        return chr(ord('a') + count-1)
    return chr(ord('a') + count -i)

class FilterModule(object):
     def filters(self):
         return {'zone': zone}

if __name__ == '__main__':
    assert zone("AB8C01") == 'a'
    assert zone("ABC01") == 'a'
    assert zone("ABC02") == 'b'
    assert zone("ABC03") == 'c'
    assert zone("ABC01",2) == 'a'
    assert zone("ABC02",2) == 'b'
    assert zone("ABC03",2) == 'a'
    assert zone("ABC01",2, "ap-northeast-2") == 'a'
    assert zone("ABC02",2, "ap-northeast-2") == 'c'
    assert zone("ABC03",2, "ap-northeast-2") == 'a'
