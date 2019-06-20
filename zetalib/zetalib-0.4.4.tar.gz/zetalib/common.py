from __future__ import absolute_import
from sage.all import Infinity

from multiprocessing import cpu_count

# paths of programs. By default use programs in $PATH.
libcrunch = None
normaliz = "normaliz"
count = "count"

ncpus = cpu_count()
debug = False
disklist = False

symbolic = False

dict_polynomial = True
save_memory = False

_alt_ncpus = None
optimisation_level = 1
addmany_dispatcher = 'numerator'
symbolic_count_varieties = []

_simplify_bound = Infinity

# The plumber tries to prevent leaks. He does this by e.g. avoiding libsingular.
plumber = True
