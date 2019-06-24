# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   ven 01 gen 2016 16:33:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018, 2019 Lele Gaifax
#

from __future__ import unicode_literals

from logging import getLogger
from os.path import abspath, dirname, exists, isabs
import sys

import pkg_resources

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import object_mapper, sessionmaker

from ruamel import yaml

from . import File, TSV, resolve_class_name
from .entity import Entity


OK, LOAD_ERROR, LOAD_EXCEPTION, PRELOAD_EXCEPTION, POSTLOAD_EXCEPTION = range(5)

logger = getLogger(__name__)


def load(fname, session, dry_run=False, delete=False, save_new_instances=False,
         adaptor=None, show_progress=False):
    """Load a single YAML file.

    :param fname: the name of the YAML file to load
    :param session: the SQLAlchemy session
    :param dry_run: whether to commit data at the end
    :param delete: whether instances shall be deleted instead of updated
    :param save_new_instances: if given, the name of the YAML file where
                               information about created instances will be written
    :param adaptor: either None or a function
    :param show_progress: whether to emit some noise as the process goes on
    :rtype: dict
    :returns: A dictionary with loaded data, keyed by (model class, key): each
              value is a tuple (primarykey, datadict)

    This will open the given file (that should contain a UTF-8 encoded
    YAML structure) and will load/update the data into the database, or
    deleted from there.

    The `adaptor` function, if specified, will be called once for each "record"
    and has the opportunity of deliberately change its content::

        user_id = 999

        def adjust_user(cls, key, data):
            if key == ['username']:
                data['username'] = data['username'] + str(user_id)
                data['user_id'] = user_id
            return data

        load('testdata.yaml', session, adaptor=adjust_user)

    When `delete` is ``True``, then existing instances will be deleted
    from the database instead of created/updated.

    If `save_new_instances` is given, it's a file name that will contain a YAML
    representation of the newly created instances, suitable to be used in a
    subsequent call with `delete` set to ``True``.

    When `dry_run` is ``False`` (the default) the function performs a
    ``flush()`` on the SQLAlchemy session, but does **not** commit the
    transaction.
    """

    from io import open

    if show_progress:
        from progressbar import ProgressBar, Counter, Timer, UnknownLength, DynamicMessage

        class EntityName(DynamicMessage):
            def __call__(self, progress, data):
                val = data['dynamic_messages'][self.name]
                return ' [%s]' % (val or '...loading...')

        pbar = ProgressBar(widgets=[fname, EntityName('entity'), ': ',
                                    Counter(), ' ', Timer()],
                           max_value=UnknownLength).start()
        count = 0

    stream = open(fname, 'r', encoding='utf-8')

    # Set the base directory: file paths will be considered relative
    # to the directory containing the YAML file
    File.basedir = dirname(abspath(fname))

    idmap = {}
    loader = yaml.Loader(stream)
    while loader.check_data():
        entries = loader.get_data()
        for entry in entries:
            if show_progress:
                pbar.update(entity=entry['entity'])
            model = resolve_class_name(entry['entity'])
            if 'rows' in entry:
                data = entry['rows']
            elif 'data' in entry:
                data = entry['data']
            else:
                data = []

            fields = entry.get('fields', None)
            if isinstance(data, TSV):
                data = data.read()
                if fields is None:
                    fields = data.pop(0)

            entity = Entity(model, entry['key'],
                            fields=fields,
                            data=data,
                            delete=delete)
            for e in entity(session, idmap, adaptor):
                if show_progress:
                    count += 1
                    pbar.update(count)

            if not dry_run:
                logger.debug("Flushing changes")
                session.flush()

    if show_progress:
        pbar.finish()

    if save_new_instances:
        existing_new_instances = set()
        new_new_instances = {}
        if exists(save_new_instances):
            with open(save_new_instances) as f:
                new_instances = yaml.load(f)
            for i in new_instances:
                entity = resolve_class_name(i['entity'])
                keys = i['key']
                for data in i['rows'] if 'rows' in i else i['data']:
                    key = tuple(data[key] for key in keys)
                    existing_new_instances.add((entity, key))
        else:
            new_instances = []

    result = {}
    for i in idmap.values():
        key = []
        for fname in i.entity.key:
            if '->' in fname:
                attr, _, slot = fname.partition('->')
                value = getattr(i.instance, attr)[slot]
            else:
                value = getattr(i.instance, fname)
            key.append(value)
        if len(i.entity.key) == 1:
            key = key[0]
        else:
            key = tuple(key)
        mapper = object_mapper(i.instance)
        pk = mapper.primary_key_from_instance(i.instance)

        if ((save_new_instances and i.created
             and (i.entity.model, tuple(pk)) not in existing_new_instances)):
            entity = i.entity.model.__module__ + '.' + i.entity.model.__name__
            pknames = tuple(str(c.key) for c in mapper.primary_key)
            data = new_new_instances.setdefault((entity, pknames), [])
            data.append(dict(zip(pknames, pk)))

        if len(pk) == 1:
            pk = pk[0]
        result[(i.entity.model, key)] = pk, i.data

    if save_new_instances and new_new_instances:
        for entity, pknames in sorted(new_new_instances):
            new_instances.append(dict(entity=entity, key=list(pknames),
                                      data=new_new_instances[(entity, pknames)]))
        with open(save_new_instances, 'w') as f:
            yaml.dump(new_instances, f, default_flow_style=False, allow_unicode=True)

    return result


def workhorse(uri, dry_run, echo, quiet,
              delete, save_new_instances, preload, postload, fnames):
    "Load one or more YAML file into the database."

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
        context = dict(session=session, dry_run=dry_run, fnames=fnames)
        try:
            code = compile(f.read(), preload, 'exec')
            exec(code, context)
            fnames = context['fnames']
        except Exception:
            logger.exception("Failure executing the preload script!")
            return PRELOAD_EXCEPTION
        finally:
            f.close()

    try:
        for fname in fnames:
            load(fname, session, dry_run, delete, save_new_instances,
                 show_progress=not quiet)
    except SQLAlchemyError as e:
        # PG errors are UTF-8 encoded
        emsg = str(e)
        if sys.version_info.major < 3:
            emsg = emsg.decode('utf-8')
        logger.error("Data couldn't be loaded: %s", emsg)
        return LOAD_ERROR
    except Exception:
        logger.exception("We are in trouble, unexpected error!")
        return LOAD_EXCEPTION

    if postload is not None:
        try:
            f = open(postload)
        except IOError:
            logger.error("Could not open postload script %r!" % postload)
            return POSTLOAD_EXCEPTION

        logger.debug('Executing postload script %r...', postload)
        context = dict(session=session, dry_run=dry_run, fnames=fnames)
        try:
            code = compile(f.read(), postload, 'exec')
            exec(code, context)
        except Exception:
            logger.exception("Failure executing the postload script!")
            return POSTLOAD_EXCEPTION
        finally:
            f.close()

    if not dry_run:
        if not quiet:
            logger.info("Committing changes")
        session.commit()

    return OK


def path_spec(ps):
    if isabs(ps) or ':' not in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    return pkg_resources.resource_filename(pkgname, subpath)


def main():
    import locale
    import logging
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(
        description="Load and/or update DB model instances.",
        epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("datafile", nargs="+", type=path_spec,
                        help="The YAML data file to load. It may be either a plain"
                        " file name, or a package relative path like"
                        " “package.name:some/file”.")
    parser.add_argument("-u", "--sqlalchemy-uri", type=str, metavar="URI",
                        help="Specify the SQLAlchemy URI.", default=None)
    parser.add_argument("-D", "--delete", default=False, action="store_true",
                        help="Delete existing instances instead of creating/"
                        "updating them. You better know what you are doing!")
    parser.add_argument("-s", "--save-new-instances", type=str, metavar='FILE',
                        help="Save new instances information into given YAML file,"
                        " preserving it's previous content.")
    parser.add_argument("-p", "--preload", type=path_spec, metavar='SCRIPT',
                        help="Execute the given Python script before loading the"
                        " data files. It may be either a plain file name or a package"
                        " relative path like “package.name:some/file”.")
    parser.add_argument("-P", "--postload", type=path_spec, metavar='SCRIPT',
                        help="Execute the given Python script after load but before"
                        " committing changes. It may be either a plain file name or a"
                        " package relative path like"
                        " “package.name:some/file”.")
    parser.add_argument("-n", "--dry-run", default=False, action="store_true",
                        help="Don't commit the changes to the database.")
    parser.add_argument("-e", "--echo", default=False, action="store_true",
                        help="Activate SA engine echo")
    parser.add_argument("-q", "--quiet", default=False, action="store_true",
                        help="Be quiet, emit only error messages")
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Activate debug logging")
    if sys.version_info.major < 3:
        parser.add_argument("-w", "--unicode-warnings", default=False,
                            action="store_true",
                            help="Activate SA unicode warnings")

    args = parser.parse_args()

    logging.basicConfig(format='%(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)

    if args.sqlalchemy_uri is None:
        print("You must specify the SQLAlchemy URI, example:")
        print("  python %s -u postgresql://localhost/dbname data.yaml"
              % sys.argv[0])

        return 128

    if sys.version_info.major < 3 and args.unicode_warnings:
        import warnings
        from sqlalchemy.exc import SAWarning

        warnings.filterwarnings(
            'ignore', category=SAWarning,
            message="Unicode type received non-unicode bind param value")

    return workhorse(args.sqlalchemy_uri, args.dry_run, args.echo, args.quiet,
                     args.delete, args.save_new_instances,
                     args.preload, args.postload, args.datafile)


if __name__ == '__main__':
    sys.exit(main())
