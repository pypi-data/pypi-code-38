from __future__ import unicode_literals
from __future__ import absolute_import
from allpairspy import AllPairs


class TestPairwise(object):
    def __init__(self):
        self.data = {}
    
    def test(self):
        # run all '_test*' methods
        tests = [f for f in dir(self) if f.startswith('_test')]
        if not tests:
            return
        pairwise = AllPairs([tests, list(self.data.keys())], filter_func=self.is_valid_combination)

        # code to make allpairs and nose play nicely with each 
        # other; maybe wrap in a nose plugin some day?
        for (test_func, data) in pairwise:
            # http://somethingaboutorange.com/mrl/projects/nose/0.11.1/writing_tests.html#test-generators
            def named_test(*args, **kwargs):
                if not getattr(self,'app',None):
                    self.setUp()
                return getattr(self,test_func)(*args, **kwargs)
            named_test.description = (self.__class__.__module__
                                      + '.' + self.__class__.__name__
                                      + '.' + test_func
                                      + '(%s)' % ','.join([data,]))
            #named_test.setup = self.setUp
            #named_test.teardown = self.tearDown
            yield named_test, data
    
    def is_valid_combination(self, row):
        return True

