# -*- encoding: utf-8 -*-

"""
:mod:`taika.taika`
==================
"""
import logging
import sys
from importlib import import_module
from pathlib import Path

import ruamel.yaml as yaml

from taika import frontmatter
from taika.events import EventManager
from taika.utils import add_syspath
from taika.utils import pretty_json

__all__ = ["read_conf", "write_file", "read_file"]

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("taika")

TAIKA_CONF = "{source}/taika.yml"

DEFAULT_EXTENSIONS = ""
DEFAULT_EXTENSIONS_PATH = ""


class Taika(object):
    """Taika main class.

    Attributes
    ----------
    source : :class:`pathlib.Path`
    destination : :class:`pathlib.Path`
    events : :class:`taika.events.EventManager`
    config : dict
    documents : list
    """

    def __init__(self, source, destination, conf_path=None):
        """Read all RST files from `source`, parse them and write them back as HTML in `dest`.

        Parameters
        ----------
        source : str
            The path to the source directory.
        dest : str
            The path where the parsed files will be writed.
        conf_path : str, optional (default=None)
            The path where the configuration file lives. If :code:`None`, the default path
            will be used.

        Notes
        -----
        By default, this functions maintains the `source` structure in `dest`.
        """
        self.documents = []
        self.events = EventManager()

        if conf_path is None:
            conf_path = TAIKA_CONF

        conf_path = conf_path.replace("{source}", str(source))
        self.config = read_conf(conf_path)

        self.import_extensions()
        self.source = Path(source)
        self.destination = Path(destination)

    def import_extensions(self):
        """Load the configuration and extensions."""
        extension_paths = self.config.get("extension_paths", DEFAULT_EXTENSIONS_PATH)
        extensions = self.config.get("extensions", DEFAULT_EXTENSIONS)

        LOGGER.debug(f"extension_paths: {extension_paths}")
        LOGGER.debug(f"extensions: {extensions}")

        # Don't create byte-code, we want the extensions folders be clean.
        sys.dont_write_bytecode = True
        with add_syspath(extension_paths):
            for ext in extensions:
                import_module(ext).setup(self)
        sys.dont_write_bytecode = False

    def process(self):
        """Run :meth:`Taika.read` and :meth:`Taika.write`."""
        self.documents = self.read(self.source)
        self.events.call("site-post-read", self)
        self.write(self.documents, self.destination)

    def read(self, source):
        """Read all the files *recursively* from a `source` directory and load them as dictionaries.

        Parameters
        ----------
        source : :class:`pathlib.Path`
            The source directory where the documents are read from.

        Returns
        -------
        documents : list
            A list of dictionaries that represent documents.
        """
        documents = []
        for path in source.glob("**/*"):
            if path.is_dir():
                continue

            document = read_file(path)
            self.events.call("doc-post-read", self, document)
            documents.append(document)
        return documents

    def write(self, documents, destination):
        """Call `taika.taika.write_file` for each document on `documents` with `destination`.

        Parameters
        ----------
        documents : list
            A list of dictionaries that represent documents.
        destination : str or :class:`pathlib.Path`
            The destination directory.
        """
        for document in documents:
            write_file(document, destination)


def read_conf(conf_path):
    """Read the configuration file `conf_path`. It should be an INI style configuration.

    Parameters
    ----------
    conf_path : str
        The path to the configuration file to be readed.

    Returns
    -------
    conf : `configparser.ConfigParser`
        An instance of a ConfigParser which holds the configuration.

    Raises
    ------
    SystemExit
        If `conf_path` is not a file.
    """
    conf_path = Path(conf_path)
    if not conf_path.is_file():
        LOGGER.critical(f"The configuration file {conf_path} is not a file. Exiting...")
        exit(1)
    else:
        with open(conf_path) as fd:
            conf = yaml.safe_load(fd)

    LOGGER.debug(pretty_json(conf))

    return conf


def read_file(path):
    """Read `path` and return the document as a dictionary.

    Parameters
    ----------
    path : str or :class:`pathlib.Path`
        A path to a file to be read.

    Returns
    -------
    document : dict
        A dictionary that holds the information of the document read from `path`.
    """
    path = Path(path)

    LOGGER.debug("Reading: %s", path)

    with open(path, "rb") as fd:
        raw_content = fd.read()
    metadata, content = frontmatter.parse(raw_content)
    document = {
        "path": path.relative_to(path.parts[0]),  # the first part is the source directory
        "url": path.relative_to(path.parts[0]),
        "content": content,
        "raw_content": raw_content,
    }

    document.update(metadata)

    return document


def write_file(document, destination):
    """Given a `document` and a destionation, write `document.content` in the destination.

    Parameters
    ----------
    document : dict
        A dictionary representing a document. Should have ``content`` and ``url``.
    destination : str or :class:`pathlib.Path`
        The destination directory where the document will be written.

    Raises
    ------
    KeyError
        If the document doesn't have ``content`` or ``url``.
    """
    destination = Path(destination)

    path = document["url"]
    content = document["content"]

    path = destination.joinpath(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    try:
        with open(path, "wb") as fd:
            fd.write(content)
        LOGGER.debug("Writing: '%s' as bytes.", path)
    except TypeError:
        with open(path, "w", encoding="utf-8") as fd:
            fd.write(content)
        LOGGER.debug("Writing: '%s' as string.", path)
