from collections import OrderedDict, UserDict
import re

__all__ = ['Struct']


def safe_convert_to_struct(value, nested=False):
    """Convert the following to Structs:
       - dicts
       - list elements that are dicts
       - ???

    This function is harmless to call on un-handled variables.
    """
    direct_converts = [dict, OrderedDict, UserDict]
    if type(value) in direct_converts:
        # Convert dict-like things to Struct
        value = Struct(value, nested=nested)
    elif isinstance(value, list):
        # Process list elements
        value = [safe_convert_to_struct(z, nested=nested) for z in value]
    elif isinstance(value, tuple):
        # Process list elements
        value = tupe([safe_convert_to_struct(z, nested=nested) for z in value])

    # Done
    return value



class Struct():
    """Ordered namespace class
    """

    # Regular expression pattern for valid Python attributes
    # https://docs.python.org/3/reference/lexical_analysis.html#identifiers
    _valid_key_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_]*')
    _special_names = ['_odict']
    _repr_max_width = 13

    def __init__(self, *args, nested=False, **kwargs):
        """Ordered namespace class
        """
        self.__dict__['_odict'] = OrderedDict()
        self.__dict__['_nested'] = nested
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        """Update self with new content
        """
        d = {}
        d.update(*args, **kwargs)

        for key, value in d.items():
            self[key] = value

    def _valid_key(self, key):
        """Return True if supplied key string serves as a valid attribute name: alphanumeric strings
        beginning with a letter.  Leading underscore not allowed.  Also test for conflict with protected
        attribute names (e.g. dict class instance methods).
        """
        if not isinstance(key, str):
            # attributes must be a string
            return False
        elif hasattr({}, key):
            # attributes cannot be same as existing dict method
            return False
        elif key in self._special_names:
            # attributes cannot be same as pre-identified special names
            return False
        else:
            # attributes must match valid key pattern
            return self._valid_key_pattern.match(key)

    def asdict(self):
        """Return a recursive dict representation of self
        """
        d = self._odict

        for k,v in d.items():
            if isinstance(v, Struct):
                d[k] = v.asdict()

        return d

    #--------------------------------
    # Expose standard dict methods
    def items(self):
        return self._odict.items()

    def keys(self):
        return self._odict.keys()

    def values(self):
        return self._odict.values()

    def pop(self, key):
        return self._odict.pop(key)

    def copy(self):
        return self._odict.copy()

    #--------------------------------
    # Expose essential dict internal methods
    def __setattr__(self, key, value):
        """Set an item with dot-style access while testing for invalid names
        """
        if not self._valid_key(key):
            raise AttributeError('Invalid key/attribute name: {}'.format(key))

        try:
            self[key] = value
        except KeyError as e:
            raise AttributeError(e)

    def __setitem__(self, key, value):
        if not self._valid_key(key):
            raise KeyError('Invalid key/attribute name: {}'.format(key))

        if self._nested:
            self._odict[key] = safe_convert_to_struct(value, nested=True)
        else:
            self._odict[key] = value

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getattr__(self, key):
        return self._odict[key]

    def __getitem__(self, key):
        return self._odict[key]

    def __delitem__(self, key):
        del self._odict[key]

    def __delattr__(self, key):
        del self._odict[key]

    def __iter__(self):
        return self._odict.__iter__()

    def __len__(self):
        return self._odict.__len__()

    def __contains__(self, key):
        return self._odict.__contains__(key)

    def __eq__(self, other):
        return self._odict.__eq__(other)

    def __ne__(self, other):
        return self._odict.__ne__(other)

    def __repr__(self):
        if self:
            return '%s(%r)' % (self.__class__.__name__, self.items())
        else:
            return '%s()' % (self.__class__.__name__,)

    def __dir__(self):
        """http://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion
        https://amir.rachum.com/blog/2016/10/05/python-dynamic-attributes
        """
        return super().__dir__() + [str(k) for k in self._odict.keys()]

    def _repr_pretty_(self, p, cycle):
        """Derived from IPython's dict and sequence pretty printer functions,
        https://github.com/ipython/ipython/blob/master/IPython/lib/pretty.py
        """
        if cycle:
            p.text('{...}')
        else:
            delim_start = self.__class__.__name__ + '{'
            delim_end = '}'

            with p.group(indent=len(delim_start), open=delim_start, close=delim_end):
                # Loop over items
                for ix, (key, value) in p._enumerate(self.items()):
                    p.break_()

                    key_txt = '{:s}: '.format(key)
                    L = len(key_txt)

                    p.indentation += L
                    p.text(key_txt)
                    p.pretty(value)
                    p.text(',')
                    p.indentation -= L

                p.break_()

#------------------------------------------------

if __name__ == '__main__':
    pass
