"""
:mod:`taika.ext.collections` -- Grouping content
================================================

This extension groups documents using patterns specified by the user. It also order those
documents using certain keys specified by the user.

It uses the patterns listed from top to bottom, the documents not included in the first
pattern are not matched against the second pattern, so be liberal in the first pattern
and more restricted at the bottom. Also, if the pattern starts with ``!`` (exclamation mark)
the documents matching will be excluded. For example:

.. code-block:: yaml

    collections:
    posts:
      patterns:
        - "posts/*" # Include all under posts
        - "!posts/index.rst" # Ignore posts/index.rst

Event
-----

This extension is subscribed to the :data:`site-post-read` event.

Process
-------

#. Setup where the ``collections`` keys is retrieved.
#. When the extension is called, scans the documents checking their ``path``.
#. If ``path`` matches the patterns provided, it's added to the collection.
#. Finally, the attribute ``collections`` is created on :class:`taika.Taika`.

Configuration
-------------

.. code-block:: yaml

    # Match all but the index.rst file on posts/
    collections:
      posts:
        patterns:
          - "posts/*" # Include all under posts
          - "!posts/index.rst" # Ignore posts/index.rst

.. data:: collections (dict)

    Default: **{}**

    A dictionary where each key specifies the name of the collection.

.. data:: collection.patterns (list)

    Default: [''] (empty string)

    The patterns to be used in order to group the files. By default, it matches nothing.

Classes and Functions
---------------------
"""
import fnmatch
import logging
from collections import defaultdict

COLLECTIONS_DEFAULT = {}
DEFAULT_PATTERNS = [""]

LOGGER = logging.getLogger(__name__)


def match(path, patterns, reverse_character="!"):
    for pattern in patterns:
        match = fnmatch.fnmatch(path, pattern.lstrip(reverse_character))
        if pattern.startswith(reverse_character):
            match = not match

        if not match:
            return False

    return True


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
        for collection_name, collection_options in config.items():
            patterns = collection_options.get("patterns", DEFAULT_PATTERNS)
            included = match(document["path"], patterns)
            if included:
                LOGGER.debug(f"Document '{document['path']}' --> Collection '{collection_name}'.")
                collections[collection_name].append(document)

    return collections


def setup(site):
    collector = Collector(site.config)
    site.events.register("site-post-read", collector.organize)
