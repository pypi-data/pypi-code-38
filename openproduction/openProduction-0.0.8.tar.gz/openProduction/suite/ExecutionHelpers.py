from openProduction.suite import TestSuite
from functools import wraps

def skipIf(_lambda):
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *f_args, **f_kwargs):
            if callable(_lambda):
                if _lambda(self) == False:
                    return f(self, *f_args, **f_kwargs)
                else:
                    return TestSuite.ExecutionResult.SKIP
            else:
                if _lambda:
                    return TestSuite.ExecutionResult.SKIP
        return wrapped
    return wrapper