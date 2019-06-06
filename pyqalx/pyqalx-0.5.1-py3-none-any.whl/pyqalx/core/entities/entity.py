from itertools import zip_longest

from pyqalx.core.errors import QalxEntityNotFound, QalxAPIResponseError, \
    QalxEntityTypeNotFound


class QalxListEntity(dict):
    """
    Simple wrapper around a pyqalxapi_dict so we can keep extra keys
    on the API list response.  Instantiates each entity in `data` to the
    correct QalxEntity subclass
    """
    def __init__(self, child, pyqalxapi_list_response_dict):
        """
        :param child: A `QalxEntity` subclass that all `data` should be
                    instantiated as
        :param pyqalxapi_list_response_dict: A dict that gets returned from
                                             a pyqalxapi list endpoint.  This
                                             should at minimum have a `data`
                                             key but may have other keys which
                                             we preserve
        """
        super().__init__(pyqalxapi_list_response_dict)

        self.child = child
        if not issubclass(self.child, (QalxEntity, )):
            raise QalxEntityTypeNotFound(f'Expected `child` to be a subclass of '
                                         f'`QalxEntity`.  Got `{self.child}`')
        if 'data' not in pyqalxapi_list_response_dict or \
                not isinstance(pyqalxapi_list_response_dict['data'], list):
            raise QalxAPIResponseError('Expected `data` key in '
                                       '`pyqalxapi_list_response_dict` and for'
                                       ' it to be a list')
        # Cast all the entities in data to be an instance of `self.child`
        self['data'] = [self.child(e) for e in pyqalxapi_list_response_dict['data']]  # noqa

    def __str__(self):
        return f"[{self.child.entity_type} list]"


class QalxEntity(dict):
    """Base class for qalx entities_response.

    QalxEntity children need to be populated with either a `requests.models.Response` which is the type returned
    by the methods on `pyqalxapi.api.PyQalxAPI` or with a `dict`.

    Entities will behave exactly like a `dict`. For example:

    >>> class AnEntity(QalxEntity):
    ...     pass
    >>> c = AnEntity({"guid":"123456789", "info":{"some":"info"}})
    >>> c['guid']
    '123456789'

    :param pyqalxapi_dict: a 'dict' representing a qalx entity object to populate the entity
    :type pyqalxapi_dict: dict
    """
    entity_type: str

    def __init__(self, pyqalxapi_dict):
        super().__init__(pyqalxapi_dict)

    def __str__(self):
        return f"[{self.entity_type}] {self['guid']}"

    @classmethod
    def _chunks(cls, _iterable, chunk_size, fillvalue=None):
        """
        Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        Taken from the itertools documentation
        """
        args = [iter(_iterable)] * chunk_size
        return zip_longest(fillvalue=fillvalue, *args)
