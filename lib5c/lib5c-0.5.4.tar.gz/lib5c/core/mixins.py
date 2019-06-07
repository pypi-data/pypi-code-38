import pickle


class Picklable:
    """
    Mixin class for providing easy reading and writing of instances to disk via
    the pickle module.
    """

    @classmethod
    def from_pickle(cls, filename):
        """
        Create a new instance of the class from a pickle file.

        Parameters
        ----------
        filename : str
            String reference to a pickle file to read from.

        Returns
        -------
        cls
            Unpickled instance.
        """
        with open(filename, 'rb') as handle:
            ob = pickle.load(handle)
        if type(ob) is not cls:
            raise ValueError('Pickled object of incorrect type.')
        return ob

    def to_pickle(self, filename):
        """
        Write this instance to a pickle file.

        Parameters
        ----------
        filename : str
            String reference to the file to write this instance to.
        """
        with open(filename, 'wb') as handle:
            pickle.dump(self, handle)


class Annotatable:
    """
    Mixin class for storing and accessing arbitrary annotation information on
    object instances.

    Attributes
    ----------
    data : dict
        Dict to store arbitrary annotation data. Typically, the keys will be
        strings.

    Notes
    -----
    This mixin requires initialization. Subclasses must explicitly call
    ::

        Annotatable.__init__(self)

    somewhere in their constructor.

    When a subclass's bound functions return a new instance, the following
    guidelines are recommended:

        * addition/summing operations: create a new dict and update it
        * other operations: copy a reference to ``data`` into the new instance
    """

    def __init__(self):
        """
        Constructor.
        """
        self.data = {}

    def __str__(self):
        r"""
        Get a string representation of the data in the ``data`` attribute.

        Returns
        -------
        str
            String representation of ``data``.

        Notes
        -----
        Subclasses can use the following pattern to access this function::

            class SomeClass(object, Annotatable):
                ...
                def __str__(self):
                    str_repr = 'SomeClass object'
                    str_repr += '\nAnnotation:'
                    str_repr += Annotatable.__str__(self)
                    return str_repr

        but are welcome to ignore it or implement their own formatting.
        """
        str_repr = ''
        for key in self.data:
            str_repr += '\n\t%s: %s' % (key, self.data[key])
        return str_repr

    def set_data(self, data):
        """
        Overwrite this instance's ``data`` attribute with a passed dict.

        Parameters
        ----------
        data : dict
            The dict to put in this instance's ``data`` attribute.
        """
        self.data = data

    def get_data(self):
        """
        Get this instance's ``data`` attribute.

        Returns
        -------
        dict
            This instance's ``data`` attribute.
        """
        return self.data

    def set_value(self, key, value):
        """
        Set the value for a specific key in this instance's ``data`` attribute.

        Parameters
        ----------
        key : str
            The key to set.
        value : any
            The value to store.
        """
        self.data[key] = value

    def get_value(self, key):
        """
        Get the value of some key in data. This is equivalent to a get-or-None
        function for ``data[key]``.

        Parameters
        ----------
        key : str
            The key to search for in this instance's ``data``.

        Returns
        -------
        any
            The value of ``data[key]``, or None if the key does not exist.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, num_genes=10)
        >>> locus.get_value('num_genes')
        10
        >>> locus.get_value('num_ctcf_sites') is None
        True
        """
        if key in self.data:
            return self.data[key]
        else:
            return None


class Loggable:
    """
    Mixin class for supporting object event logging.

    Attributes
    ----------
    log : list of str
        Each string in the list describes an event in this object's history.

    Notes
    -----
    This mixin requires initialization. Subclasses must explicitly call
    ::

        Loggable.__init__(self)

    somewhere in their constructor.

    When a subclass's bound functions return a new instance, the following
    guidelines are recommended:

        * addition/summing operations: use the empty log of the new instance
        * other operations: copy a reference to ``log`` into the new instance
    """

    def __init__(self):
        """
        Constructor.
        """
        self.log = []

    def log_event(self, event):
        """
        Add an event to the log.

        Parameters
        ----------
        event : str
            A string describing the event.
        """
        self.log.append(event)

    def get_log(self):
        """
        Get this instance's log.

        Returns
        -------
        list of str
            This instance's log.
        """
        return self.log

    def print_log(self):
        """
        Print this instance's log to the console.
        """
        for event in self.log:
            print event
