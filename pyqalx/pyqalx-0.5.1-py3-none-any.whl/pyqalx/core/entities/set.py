from pyqalx.core.entities import QalxEntity


class Set(QalxEntity):
    """A set is simply a collection of items.

    They are mapped with keys so that you can retrieve specific items from the set later:

    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> dims = qalx.item.add(data={"height":5, "width":5}, meta={"shape":"square"})
    >>> steel = qalx.item.add_file("path/to/316_datasheet.pdf",
    ...                             data={"rho":8000, "E":193e9},
    ...                             meta={"library":"materials", "family":"steel", "grade":"316"})
    >>> steel_square_set = qalx.add.set(items={"shape":dims, "material":steel}, meta={"profile":"square_steel"})

    As with items we can then use the ``find_one`` and ``find`` methods to search for sets and easily get the item data:

    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> my_set = qalx.set.find_one(meta="profile=square_steel")
    >>> youngs_mod = my_set.get_item_data("material")['E']

    .. note::
        Sets store a **reference to an item** rather than a copy of the item. Changes to the item will be reflected in
        all sets containing that item.

    """
    entity_type = 'set'
    
    def get_item_data(self, item_key):
        """
        helper method to get data from an item in the set

        :param item_key: key on the set to add the item as
        :type item_key: str
        :return: dict or None if key is missing
        """
        if self['items'].get(item_key):
            return self['items'].get(item_key)['data']
        else:
            return None
