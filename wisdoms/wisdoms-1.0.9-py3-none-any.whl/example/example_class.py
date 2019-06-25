'''
第二种方法：如果模块是以class组织代码的
```
from wisdom.example_class import my_class
mc=my_class()
mc.hello()
mc.world()
```
'''
import logging


class ExampleClass:
    name = 'sky is blue'
    def __init__(self):
        self.age = 10

    def my_hello(self):
        print('i am a object method')

    def hello(self):
        print('i am a object method')

    @staticmethod
    def hello():
        print('hello{}'.format('world,staticmethod'))

    @classmethod
    def world(cls):
        print('{},world'.format('hello'))

    @classmethod
    def hello(cls):
        print('hello{}'.format('world,classmethod'))


