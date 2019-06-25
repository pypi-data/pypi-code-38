'''Demo Section Results & Gotos

This AEtest script is intended to demonstrate how users can manually assign
results to each section, provide a reason for that result, and as well how to
perform a goto action after providing a result.

Run this jobfile in standalone:
    
    bash$ python demo_results.py

'''

from pyats import aetest

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def subsection(self):
        self.passed('demoing passed result api')

class Testcase(aetest.Testcase):

    @aetest.setup
    def setup(self):
        self.skipped('demoing skipped result api')

    @aetest.test
    def test(self): 
        assert 1 + 2 == 3

    @aetest.cleanup
    def cleanup(self):
        try:
            api_doesnt_exist()
        except:
            self.errored('api does not exist', goto = ['common_cleanup'])

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def subsection(self):
        self.failed('demoing failed result api', goto = ['exit'])

    @aetest.subsection
    def subsection_not_run(self):
        pass


# standalone execution
if __name__ == '__main__':
    aetest.main()