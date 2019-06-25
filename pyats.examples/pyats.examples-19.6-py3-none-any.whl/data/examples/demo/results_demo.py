'''Simple Results Code

This script code demonstrate how result codes in pyATS are singletons, and how
they can be rolled up together, the various attributes, etc.

You can run this script directly, but it's better to copy paste each command
into a python interpreter shell and observe/interact with the code.
'''

from pyats.results import (Passed, Errored, Failed, Skipped, 
                         Aborted, Blocked, Passx)


Passed + Failed
# Failed

Failed + Errored
# Errored

sum([Failed, Errored, Aborted])
# Aborted

Skipped.tims
# 'dropped'

Skipped.code
# 4


