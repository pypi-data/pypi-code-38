
# Here we're trying to import the mystery package (it's "pygments" this time).
# If it exists, overwrite 'mystery' in 'sys.modules'. Else, print there was an error.
import sys
try:
    import pygments
except ImportError as error:
    print('Internal error:', error)
    print("The mystery package wasn't playing nice. Sorry!")
    print('Hint: you can always try to reinstall mystery and get a different package!')
    sorry = 'try reinstalling mystery and get a different package!'
else:
    sys.modules['mystery'] = pygments
sys.modules['mystery'].__mystery_init_py__ = __file__
sys.modules['mystery'].__mystery_package_name__ = 'pygments'
del sys  # We care about this only when mystery fails (and even that's inconsequential).
