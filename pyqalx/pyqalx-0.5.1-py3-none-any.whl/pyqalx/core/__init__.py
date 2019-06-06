"""
Sessions & Adapters
~~~~~~~~~~~~~~~~~~~

The best way to interface between entities and qalx is with the `session` object.
There are also lower-level individual adapters if required.

.. _qalxsession:

.. automodule:: pyqalx.core.adapters
    :members:

Entities
~~~~~~~~
Root entities - these are children of ``dict`` but with special methods

.. _bot_entity:
.. automodule:: pyqalx.core.entities.bot
    :members:

.. _qalx_entity:
.. automodule:: pyqalx.core.entities.entity
    :members:

.. _group_entity:
.. automodule:: pyqalx.core.entities.group
    :members:

.. _item_entity:
.. automodule:: pyqalx.core.entities.item
    :members:

.. _queue_entity:
.. automodule:: pyqalx.core.entities.queue
    :members:

.. _set_entity:
.. automodule:: pyqalx.core.entities.set
    :members:

.. _worker_entity:
.. automodule:: pyqalx.core.entities.worker
    :members:

.. _blueprint_entity:
.. automodule:: pyqalx.core.entities.blueprint
    :members:


Logging
~~~~~~~

.. automodule:: pyqalx.core.log
    :members:


Signals
~~~~~~~

.. automodule:: pyqalx.core.signals
    :members:

Errors
~~~~~~

.. automodule:: pyqalx.core.errors
    :members:



"""

from pyqalx.core.errors import QalxNoGUIDError, QalxNoInfoError

