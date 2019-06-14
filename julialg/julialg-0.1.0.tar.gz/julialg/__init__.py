__MAJOR__ = 0
__MINOR__ = 1
__MICRO__ = 0
__VERSION__ = (__MAJOR__, __MINOR__, __MICRO__)
__version__ = '.'.join(str(n) for n in __VERSION__)
__github_url__ = 'http://github.com/JWKennington/julialg'


from julialg.array import JulArray
from julialg.core import JulialgError