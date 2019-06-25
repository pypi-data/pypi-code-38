import sys
import inspect

from .aereport import AEReporter
from .default import StandaloneReporter

class ReporterRedirect(object):

    # declare module as infra
    # note - declaring here because module = obj
    __aetest_infra__ = True
    
    def __init__(self):
        # create default reporter
        self.__reporter__ = StandaloneReporter()

    def __getattr__(self, attr):
        '''Built-in __getattr__ function

        Called when getattr() this object and the object doesn't exist. Used
        to redirect calls to the actual __reporter__ object

        '''
        
        return getattr(self.__reporter__, attr)

    def change_to(self, reporter):
        self.__reporter__ = reporter

    def __setattr__(self, name, value):
        '''Built-in __setattr__ function

        This function redirects setting reporter attributes to the encapsulated
        __reporter__ instance (the actual reporter object).

        Because this object is an ultimate redirect to the actual reporter 
        instance, all of its own internal variables should begin with _ or __ to
        avoid name clashing.
        '''

        if name.startswith('_'):
            # any attributes with _ or __ is internal to me
            return super().__setattr__(name, value)
        else:
            # everything else belongs to __reporter__ object instance
            return setattr(self.__reporter__, name, value)

extras = inspect.getmembers(sys.modules[__name__], callable)

sys.modules[__name__] = redirector = ReporterRedirect()

for name, value in extras:
    setattr(redirector, name, value)

# hardwire all module hidden attributes to redirector instance
redirector.__file__    = __file__
redirector.__loader__  = __loader__
redirector.__package__ = __package__
redirector.__name__    = __name__
redirector.__path__    = __path__
redirector.__spec__    = __spec__
redirector.__doc__     = __doc__


