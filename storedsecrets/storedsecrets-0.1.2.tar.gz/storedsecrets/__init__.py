r"""storedsecrets is a module implementing a simple approach to keep
your secrets (API keys, passwords, ...) outside of your project files,
so that you can protect them better (e.g. in an encrypted archive, or
any form of external volume), and you don't leak them accidentally
through your favorite versioning tool and platform.

:mod:`storedsecrets` exposes a `StoredSecrets` class to handle your secrets.

Typical usage:

    >>> import storedsecrets
    >>> my_secrets = storedsecrets.StoredSecrets("mysecretfile.json")
    >>> API_KEY = my_secrets.get('API_KEY')

If the path of the file is not absolute, it will be searched for in
the directory named in env var ``SECRETS``, or in ``~/etc/secrets`` by
default.

TO BE CONTINUED

"""

__version__ = '0.1.2'

__all__ = ['StoredSecrets']

__author__ = 'Benjamin THOMAS <bth0mas@free.fr>'


# TODO: split this to allow use of different formats

# TODO: implement 'save()' and 'set()' ?

# TODO: at some point, think about using a collection.abc.Mapping or
# MutableMapping to implement this class; see
# https://stackoverflow.com/a/3387975

import json
import os

class StoredSecrets():
    """Stored Secrets handling class

    Attributes
    ----------
    None public

    Methods
    -------
    load(): (re)load the content of the secrets file
    keys(): get a list (NOT a dict keys) of keys as strings
    get(key, [default]): fetch for a particular key, optionally defaulting

    """

    ### Private attributes:
    ###  _source   str  to store the (full) path of the secrets file
    ###  _meta     dict to store the __meta__ section of the secrets file
    ###  _secrets  dict to store the secrest themselves
    
    def __init__(self, source="default.json"):
        """Parameters:
        -----------
        source: str, optional

            The file to load; if relative, will be fetched from
            "secrets" directory of the user (``SECRETS`` env var, or
            ``~/etc/secrets``)
        """ 
        if os.path.isabs(source):
            self._source = source
        else:
            self._source = os.path.join(self._defaulthome(), source)

        self.load()
            

    def _defaulthome(self):
        """Private class method.
        Parameters: none.

        Returns the default home of secrets, either content of the
        ``SECRETS`` env var, or ``~/etc/secrets`` if env var is not set.
        """
        return os.getenv('SECRETS', os.path.expanduser('~/etc/secrets'))

    
    def load(self):
        """Parameters:
        -----------
        None

        Returns: Boolean
        """
        successful = True
        try:
            with open( self._source ) as f: self._secrets = json.load(f)
        except OSError:
            self._secrets = {}
            succesful = False

        # move aside the meta-information from the secrets
        self._meta = self._secrets.pop('__meta__', None)

        return successful

    
    def keys(self):
        """Parameters: None
        Returns: a list of the available keys, as strings.
        """
        return list(self._secrets.keys())

    
    def get(self, key, default=None):
        """
        Parameters: 
        -----------
        key: str - the entry to look for
        default: optional - the value to return in case entry does not exist
        (by default: None)

        Returns: the entry as found, or the value of default
        """
        return self._secrets.get(key, default)

