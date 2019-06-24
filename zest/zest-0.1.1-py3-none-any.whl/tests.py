from time import time
from .all_tests import test_list

class tests:
    def __init__(self, func_to_test):
        test_list.append(self)
        self.func = func_to_test        
        self.result = None
        self.time_taken = None
        self.error = None
    
    def __call__(self, func_that_tests):
        self.test = func_that_tests
        return self.do_test

    def do_test(self):
        t_start = time()
        try:
            self.test(self.func)
        except Exception as e:
            self.result = False
            self.time_taken = None
            self.error = e
        else:
            self.result = True
            self.time_taken = time() - t_start
            self.error = None
        return self

    def __repr__(self):
        lines = []
        lines.append("Test for '{}':".format(self.func.__name__))
        if self.test.__doc__ is not None:
            lines.append("\t{0}".format(self.test.__doc__))
        lines.append("\tResult: {}".format(self.result))
        if self.result is True:
            lines.append("\tTook {} seconds".format(self.time_taken))
            lines.append("\tTest Passed.")
        else:
            lines.append("\tWith error:")
            lines.append("\t\t{}".format(self.error.__class__.__name__))
            lines.append("\t\t{}".format(self.error.__str__()))
            lines.append("\tTest Failed.")
        return "\n".join(lines)        