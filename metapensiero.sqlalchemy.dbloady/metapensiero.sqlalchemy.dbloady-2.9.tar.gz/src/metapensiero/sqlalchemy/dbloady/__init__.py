# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   mer 10 feb 2010 14:35:05 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2010-2019 Lele Gaifax
#

from os.path import join, normpath

from ruamel import yaml


def resolve_class_name(classname):
    """Import a particular Python class given its full dotted name.

    :param classname: full dotted name of the class,
                      such as "package.module.ClassName"
    :rtype: the Python class
    """

    modulename, _, classname = classname.rpartition('.')
    module = __import__(modulename, fromlist=[classname])
    return getattr(module, classname)


class File(yaml.YAMLObject):
    """Facility to read the content of an external file.

    The value of field may be loaded from an external file, given its pathname which is
    interpreted as relative to the position of the YAML file currently loading::

        - entity: cpi.models.Document
          key: filename
          data:
            - filename: image.gif
              content: !File {path: ../image.gif}

    By default the content is assumed to be a *binary*: specifying an `encoding` it will be
    loaded as *text* instead::

        - entity: cpi.models.Script
          key: filename
          data:
            - content: !File
                path: script.py
                encoding: utf-8

    Alternatively, the content may be inline, possibly compressed::

        - entity: cpi.models.Document
          key: filename
          data:
            - filename: image.gif
              content: !File
                compressor: lzma
                content: !!binary |
                  /Td6WFoAAATm1rRGAgAhA...
    """

    yaml_tag = '!File'

    basedir = None

    def __init__(self, path=None, encoding=None, content=None, compressor=None):
        self.path = path
        self.encoding = encoding
        self.content = content
        self.compressor = compressor

    def read(self):
        # PyYAML does not execute the __init__ method
        path = getattr(self, 'path', None)
        if path is None:
            content = getattr(self, 'content', None)
            if content is None:
                raise RuntimeError('The !File object requires either a "path"'
                                   ' or a "content" argument')
            compressor = getattr(self, 'compressor', None)
            if compressor is not None:
                if compressor == 'lzma':
                    from lzma import decompress
                elif compressor == 'gzip':
                    from gzip import decompress
                else:
                    raise RuntimeError('Unsupported compressor: %r' % compressor)
                content = decompress(content)
            if isinstance(content, bytes) and hasattr(self, 'encoding') is not None:
                content = content.decode(self.encoding)
        else:
            fullpath = normpath(join(self.basedir, path))
            if hasattr(self, 'encoding'):
                with open(fullpath, encoding=self.encoding) as f:
                    content = f.read()
            else:
                with open(fullpath, 'rb') as f:
                    content = f.read()

        return content


class TSV(File):
    """Facility to read the content of an external TSV__ file.

    The data rows for an entity may be loaded from an external TSV file, given its pathname
    which is interpreted as relative to the position of the YAML file currently loading,
    **and** its encoding::

        - entity: model.Countries
          key:
            - code
          rows: !TSV {path: ../data/countries.txt, encoding: utf-8}

    A value of ``\\N`` is replaced with ``None``, in the `PostgreSQL tradition`__, and other
    common ASCII escape sequences are recognized by using the `unicode_escape`__ codecs.

    __ https://en.wikipedia.org/wiki/Tab-separated_values
    __ https://www.postgresql.org/docs/11/sql-copy.html#id-1.9.3.55.9.2
    __ https://docs.python.org/3.7/library/codecs.html#text-encodings
    """

    yaml_tag = '!TSV'

    def read(self):
        content = super().read()
        return [[None if f == '\\N' else bytes(f, 'utf-8').decode('unicode_escape')
                 for f in line.split('\t')]
                for line in content.splitlines()]


class SQL(yaml.YAMLObject):
    """Raw SQL statement."""

    yaml_tag = '!SQL'

    def __init__(self, query, params=None):
        self.query = query
        self.params = params

    def fetch(self, session):
        # PyYAML does not execute the __init__ method
        try:
            query = self.query
        except AttributeError:
            raise RuntimeError('The !SQL object requires a "query" argument')
        try:
            params = self.params
        except AttributeError:
            params = None
        return session.scalar(query, params)
