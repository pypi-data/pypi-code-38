class PackingMixin(object):
    """
    Abstract view mixing for providing a method of "packing" (turning an
    object into a JSON-serialisable list or dictionary) a given type. The
    base `pack` method only packs primitive types.
    """

    def pack(self, depth=0):  # pragma: no cover
        """
        This method packs primitive types and raises a
        :class:`~exceptions.ConfigurationError` exception if a type cannot
        be packed. Override this method to pack more complex objects.
        """

        raise NotImplementedError('Method not implemented')
