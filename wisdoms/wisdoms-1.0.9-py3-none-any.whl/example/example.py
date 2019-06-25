'''
第一种方法：直接在模块中定义方法
```
import wisdom.example as we
we.hello()
```
'''
import logging
from wisdoms.commons import revert, codes, success
def hello():
    print('hello{}'.format('world'))

def world():
    print('{},world'.format('hello'))

if __name__ == '__main__':
    print(revert(codes.NOT_AUTHORIZED))
    print(success('abc'))
    print(success())