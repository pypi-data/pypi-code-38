import re

def ebs_dev(index,count=3):
    index = int(index)
    if index == 0:
        return "/dev/xvdf"
    else:
        return "/dev/xvd" + chr(ord('f') + index)


class FilterModule(object):
     def filters(self):
         return {'ebs_dev': ebs_dev}

if __name__ == '__main__':
    assert ebs_dev("0") == '/dev/xvdf'
    assert ebs_dev("1") == '/dev/xvdg'
