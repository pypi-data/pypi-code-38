
import os
import sys
from awslambda_handler.eventparser import EventParser

class Responder(object):
    """
    """
    @property
    def caller(self):
        return self.__caller

    @caller.setter
    def caller(self, event):
        self.__caller = EventParser(event).caller

    @property
    def sender(self):
        return self.__sender

    @sender.setter
    def sender(self, event):
        module_name = f'awslambda_handlers.responder.{self.caller}'
        try:
            module = __import__(self.caller, globals=globals())
            klass = getattr(module, self.caller.title())
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'404 - Could not import module {self.caller}')
        except AttributeError:
            raise AttributeError(f'404 - No attribute {self.caller.title()} in module {module}')
        self.__sender = klass(event)


    def __init__(self, event, **kwargs):
        sys.path.append(os.path.dirname(__file__))
        self.caller = event
        self.sender = event

    def __repr__(self):
        return self.caller.title()


if __name__ == '__main__':
    EVENT = {
        'StackId': 'Id234',
        'RequestType': 'Create',
        'ResourceType': 'custom',
        'ResourceProperties': {'toto': 'tata'},
        'ResponseURL': 'https://s3.amazonaws.com/'
    }
    RES = Responder(EVENT)
    print (RES)
