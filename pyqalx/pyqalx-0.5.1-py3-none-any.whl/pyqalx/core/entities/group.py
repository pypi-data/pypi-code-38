from pyqalx.core.entities import QalxEntity


class Group(QalxEntity):
    """A group is a collection of `sets <https://en.wikipedia.org/wiki/Turtles_all_the_way_down>`_.
    These are useful for sending a lot of sets to a queue and being able to track when they have all been processed.


    >>> from pyqalx import QalxSession
    >>> qalx = QalxSession()
    >>> steel = qalx.item.add_file("path/to/316_datasheet.pdf",
    ...                             data={"rho":8000, "E":193e9},
    ...                             meta={"library":"materials", "family":"steel", "grade":"316"})
    >>> steel_squares = {}
    >>> for size in range(2, 500):
    ...     dims = qalx.item.add(data={"height":size, "width":size}, meta={"shape":"square"})
    ...     steel_square_set = qalx.add.set(items={"shape":dims, "material":steel}, meta={"profile":"square_steel"})
    ...     steel_squares[size] = steel_square_set
    >>> all_squares = qalx.group.add(sets=steel_squares)

    """
    entity_type = 'group'
