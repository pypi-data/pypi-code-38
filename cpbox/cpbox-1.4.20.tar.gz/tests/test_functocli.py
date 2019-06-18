import unittest
import inspect
from cpbox.tool import functocli

class ToolA():

    def __init__(self, app, name, port):
        self.app = app
        self.name = name
        self.port = port
        print('ToolA: %s %s' % (app, name))

    def show_name(self):
        print(self.name)

    def show_port(self):
        print(self.port)

class ToolkitBase(object):

    def __init__(self):
        pass

    def base_name(self):
        print('ToolkitBase')

    @functocli.keep_method
    def version(self):
        print('1.0.0')

@functocli.merge_class(ToolA)
class Toolkit(ToolkitBase):

    def __init__(self):
        print('__init__: %s' % (self))
        self._init_tool_a()
        self.name = 'Toolkit'

    def _init_tool_a(self):
        functocli.append_cli(self, ToolA(self, 'tool-a', port=80))

    def show_cli_name(self):
        print(self.name)

if __name__ =='__main__':
    functocli.run_app(Toolkit, 'debug')
    # tool_a = ToolA(None, 'tool-a', port=80)
    # func = getattr(tool_a, 'show_name')
    # func()

