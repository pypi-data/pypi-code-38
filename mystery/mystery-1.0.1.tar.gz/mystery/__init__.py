
# I'd like not to affect the current imported modules (besides 'mystery' of course).
# Using a function's scope to contain the imports makes it less of a headache during cleanup.
import sys
def _import_guard():
    """
    Attempt to import the chosen package and add it to sys.modules.
    """
    try:
        import pillow
    except ImportError as error:
        print('Internal error:', error)
        print("The mystery package wasn't playing nice. Sorry!")
        return
    sys.modules['mystery'] = pillow
_import_guard()
del _import_guard
sys.modules['mystery'].__mystery_init_py__ = __file__
sys.modules['mystery'].__mystery_package_name__ = 'pillow'
del sys
