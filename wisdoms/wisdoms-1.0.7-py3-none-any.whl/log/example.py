'''
第一种方法：直接在模块中定义方法
```
import wisdom.example as we
we.hello()
```
'''
import logging
def hello():
    print('hello{}'.format('world'))

def world():
    print('{},world'.format('hello'))
