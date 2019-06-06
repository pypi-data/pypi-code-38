import os

import requests

from pyqalx.core.entities import QalxEntity
from pyqalx.core.errors import QalxError


class Item(QalxEntity):
    """An item is the core of qalx.

    They are structured data or a file or some combination of the two. For example:

    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> dims = qalx.item.add(data={"height":5, "width":5}, meta={"shape":"square"})
    >>> steel = qalx.item.add_file("path/to/316_datasheet.pdf",
    ...                             data={"rho":8000, "E":193e9},
    ...                             meta={"library":"materials", "family":"steel", "grade":"316"})

    We can then use the ``find_one`` and ``find`` methods to search for items

    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> steel_316_item = qalx.item.find_one(meta=["library=materials", "family=steel", "grade=316"])
    >>> steels = qalx.item.find(meta="family=steel")
    >>> squares = qalx.item.find(meta="shape=square")
    >>> quads = qalx.item.find(meta="(shape=square|shape=rectangle)")

    We can edit an item once we have retrived it and save it back to qalx

    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> my_shape = qalx.item.find_one(data=["height=5", "width=5"])
    >>> my_shape['data']['height'] = 10
    >>> my_shape['meta']['shape'] = 'rectangle'
    >>> qalx.item.save(my_shape)
    >>> # If we think that someone else might have edited my_shape we can reload it:
    >>> my_shape = qalx.item.reload(my_shape)
    """
    entity_type = 'item'
    _file_bytes = None

    def read_file(self):
        if "file" not in self.keys():
            raise QalxError("Item doesn't have file data.")
        else:
            response = requests.get(url=self['file']['url'])
            if response.ok:
                self._file_bytes = response.content
                return self._file_bytes
            else:
                raise QalxError("Error with file retrieval: \n\n" + response.text)

    def save_file(self, filepath, filename=None):
        if filename is None:
            filename = self['file']['filename']
        if self._file_bytes is None:
            self.read_file()
        with open(os.path.join(filepath, filename), "wb") as f:
            f.write(self._file_bytes)



