'''Simple Demo Script

The intention of this script is to demonstrate how to define the various
sections within AEtest.

Run this script in standalone:
    
    bash$ python demo.py
'''

from pyats import aetest

# define a common setup section
class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def subsection(self):
        pass

# define a single testcase
class Testcase(aetest.Testcase):

    @aetest.setup
    def setup(self):
        pass

    @aetest.test
    def test(self): 
        pass

    @aetest.cleanup
    def cleanup(self):
        pass

# define a common cleanup section
class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def subsection(self):
        pass


# standalone execution
if __name__ == '__main__':
    aetest.main()