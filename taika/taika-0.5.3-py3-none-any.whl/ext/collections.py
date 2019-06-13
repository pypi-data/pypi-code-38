"""
:mod:`taika.ext.collections` -- Grouping content
================================================

This extension groups documents using a pattern specified by the user. It also order those
documents using certain keys specified by the user.

.. note::

    It uses the :mod:`re` python module, so the pattern must be in regular expression format.

Event
-----

This extension is subscribed to the :data:`site-post-read` event.

Process
-------

#. Setup where the ``collections`` keys is retrieved.
#. When the extension is called, scans the documents checking their ``path``.
#. If ``path`` matches the pattern provided, it's added to the collection.
#. Finally, the attribute ``collections`` is created on :class:`taika.Taika`.

Configuration
-------------

.. code-block:: yaml

    # Match all but the index.rst file on posts/
    collections:
      posts:
        pattern: "posts/(?!index.rst).*"

.. data:: collections (dict)

    Default: **{}**

    A dictionary where each key specifies the name of the collection.

.. data:: collection.pattern (str)

    Default: '' (empty string)

    The pattern to be used in order to group the files. By default, it matches nothing.

Classes and Functions
---------------------
"""
import logging
import re
from collections import defaultdict

COLLECTIONS_DEFAULT = {}
PATTERN_DEFAULT = ""

LOGGER = logging.getLogger(__name__)


class Collector(object):
    """Main class which retrieves the configuration and the organize the documents."""

    def __init__(self, config):
        self.collections_config = config.get("collections", COLLECTIONS_DEFAULT)

    def organize(self, site):
        """Classify the documents and creates the collections attribute on `site`."""
        collections = _organize(site.documents, self.collections_config)
        site.collections = collections


def _organize(documents, config):
    collections = defaultdict(list)
    for document in documents:
        for name, options in config.items():
            pattern = options.get("pattern", PATTERN_DEFAULT)
            if re.match(pattern, str(document["path"])):
                LOGGER.debug(f"Document '{document['path']}' added to collection '{name}'.")
                collections[name].append(document)

    return collections


def setup(site):
    collector = Collector(site.config)
    site.events.register("site-post-read", collector.organize)
