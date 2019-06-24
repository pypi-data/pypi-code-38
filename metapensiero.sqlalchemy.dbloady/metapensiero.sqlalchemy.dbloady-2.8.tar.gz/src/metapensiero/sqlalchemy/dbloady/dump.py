# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data dumper
# :Created:   dom 06 mar 2016 17:48:31 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018 Lele Gaifax
#

from logging import getLogger
from inspect import isgenerator
from io import open
from itertools import chain
from os.path import isabs
import sys

import pkg_resources

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.collections import InstrumentedList

from ruamel import yaml

from . import resolve_class_name
from .entity import Entity


OK, SPEC_FILE_ERROR, PRELOAD_EXCEPTION = range(3)

logger = getLogger(__name__)

if sys.version_info.major >= 3:
    basestring = str


def dump(pivots, specs):
    """Dump database content into a YAML document.

    :param pivots: either a single instance or an iterable of them
    :param specs: an sequence of *spec entries*, each describing how a particular entity shall
                  be serialized
    :rtype: list
    :returns: a sequence of items, one for each entity declared in `specs` (and in that order),
              containing the data of the collected instances of that entity

    A *spec entry* is a dictionary containing at least an ``entity`` slot with the fully
    qualified dotted name of a SQLAlchemy mapped class and a ``key`` slot with either a single
    string or a list of strings, the name of the attributes that uniquely identity a single
    instance. Remaining fields may be listed in the ``other`` slot.
    """

    specs_by_qualname = {spec['entity']: spec for spec in specs}

    seen = set()
    entities = {}
    instances = {}

    def get_attribute(instance, attr):
        if '->' in attr:
            attr, _, slot = attr.partition('->')
            value = getattr(instance, attr)[slot]
        else:
            value = getattr(instance, attr)
        return value

    def get_identity(instance):
        klass = instance.__class__
        qualname = instance.__module__ + '.' + klass.__name__
        if qualname not in specs_by_qualname:
            return

        spec = specs_by_qualname[qualname]

        key = spec['key']
        if callable(key):
            key = key(instance)
        if isinstance(key, str):
            identity = (qualname, get_attribute(instance, key))
        else:
            assert isinstance(key, (tuple, list))
            identity = (qualname, tuple(get_attribute(instance, f) for f in key))

        return identity

    def visit(instance):
        identity = get_identity(instance)
        if identity is None:
            return

        if identity in seen:
            return instances[identity]

        seen.add(identity)

        qualname = identity[0]
        spec = specs_by_qualname[qualname]
        key = spec['key']

        if qualname in entities:
            entity = entities[qualname]
        else:
            entity = entities[qualname] = {'entity': qualname, 'key': key, 'rows': []}

        if 'fields' in spec:
            fields = entity['fields'] = spec['fields']
            if isinstance(fields, basestring):
                attributes = [fields]
            else:
                attributes = fields

            data = instances[identity] = []
        else:
            fields = None
            attributes = []

            if isinstance(key, str):
                attributes.append(key)
            else:
                attributes.extend(key)

            other = spec.get('other', [])
            if isinstance(other, basestring):
                attributes.append(other)
            else:
                attributes.extend(other)

            data = instances[identity] = {}

        entity['rows'].append(data)

        for attr in attributes:
            value = get_attribute(instance, attr)

            # Skip Nones, only if we are emitting dictionaries
            if value is None and fields is None:
                continue

            if isinstance(value, InstrumentedList):
                for i in value:
                    visit(i)
            else:
                try:
                    inspector = inspect(value)
                except NoInspectionAvailable:
                    if fields is None:
                        data[attr] = value
                    else:
                        data.append(value)
                else:
                    if inspector.is_instance:
                        value = visit(value)
                        if value is not None:
                            if fields is None:
                                data[attr] = value
                            else:
                                data.append(value)

        return data

    if isinstance(pivots, (list, tuple)) or isgenerator(pivots) or isinstance(pivots, chain):
        for pivot in pivots:
            visit(pivot)
    else:
        visit(pivots)

    return [entities[spec['entity']] for spec in specs
            if spec['entity'] in entities]


def workhorse(uri, echo, preload, specfname, outputstream):
    engine = create_engine(uri, echo=echo)
    salogger = getattr(engine.logger, 'logger', None)
    if salogger is not None:
        for h in salogger.handlers:
            salogger.removeHandler(h)
    smaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    session = smaker()

    if preload is not None:
        try:
            f = open(preload)
        except IOError:
            logger.error("Could not open preload script %r!" % preload)
            return PRELOAD_EXCEPTION

        logger.debug('Executing preload script %r...', preload)
        context = dict(session=session)
        try:
            code = compile(f.read(), preload, 'exec')
            exec(code, context)
        except Exception:
            logger.exception("Failure executing the preload script!")
            return PRELOAD_EXCEPTION
        finally:
            f.close()


    idmap = {}
    pivots = None

    with open(specfname, 'r', encoding='utf-8') as stream:
        loader = yaml.Loader(stream)
        entries = loader.get_data()
        if entries is None:
            logger.error('Could not read pivot entries from spec file')
            return SPEC_FILE_ERROR
        specs = loader.get_data()
        if specs is None:
            logger.error('Invalid spec file, should contain two documents')
            return SPEC_FILE_ERROR

    for entry in entries:
        model = resolve_class_name(entry['entity'])
        if 'rows' in entry:
            data = entry['rows']
        elif 'data' in entry:
            data = entry['data']
        else:
            data = None

        if data is not None:
            entity = Entity(model, entry['key'],
                            fields=entry.get('fields', None),
                            data=data,
                            loadonly=True)
            instances = entity(session, idmap)
        else:
            instances = iter(session.query(model))

        if pivots is None:
            pivots = instances
        else:
            pivots = chain(pivots, instances)

    result = dump(pivots, specs)

    yaml.dump(result, outputstream, default_flow_style=False)

    return OK


def path_spec(ps):
    if isabs(ps) or not ':' in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    return pkg_resources.resource_filename(pkgname, subpath)


def main():
    import locale, logging
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(
        description="Dump YAML representation of database content.",
        epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("specfile", type=path_spec,
                        help="The YAML data file to containing dump specifications."
                        " It may be either a plain file name or a package"
                        " relative path like “package.name:some/file”.")
    parser.add_argument("output", default="-", nargs='?',
                        help="Where to write the YAML dump: “-” means stdout,"
                        " the default.")
    parser.add_argument("-u", "--sqlalchemy-uri", type=str, metavar="URI",
                        help="Specify the SQLAlchemy URI.", default=None)
    parser.add_argument("-p", "--preload", type=path_spec, metavar='SCRIPT',
                        help="Execute the given Python script before loading the"
                        " spec file. It may be either a plain file name or a package"
                        " relative path like “package.name:some/file”.")
    parser.add_argument("-e", "--echo", default=False, action="store_true",
                        help="Activate SA engine echo")
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Activate debug logging")

    args = parser.parse_args()

    logging.basicConfig(format='%(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)

    if args.output == '-':
        output = sys.stdout
    else:
        output = open(args.output, 'w', encoding='utf-8')

    return workhorse(args.sqlalchemy_uri, args.echo, args.preload, args.specfile, output)


if __name__ == '__main__':
    sys.exit(main())
