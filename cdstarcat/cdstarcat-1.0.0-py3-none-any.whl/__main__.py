"""
Main command line interface of the cdstarcat package.

The basic invocation looks like

    cdstarcat [OPTIONS] <command> [args]

"""
import sys
from collections import Counter
from itertools import groupby, chain
import os

from clldutils.clilib import ArgumentParserWithLogging, command
from clldutils.markup import Table

from cdstarcat import Catalog, OBJID_PATTERN


@command()
def cleanup(args):
    """
    cdstarcat cleanup

    Deletes objects with no bitstreams from CDSTAR and the catalog.
    """
    with _catalog(args) as cat:
        n, d, r = len(cat), [], []
        for obj in cat:
            if not obj.bitstreams:
                if obj.is_special:
                    print('removing {0} from catalog'.format(obj.id))
                    r.append(obj)
                else:
                    print('deleting {0} from CDSTAR'.format(obj.id))
                    d.append(obj)
        for obj in d:
            cat.delete(obj)
        for obj in r:
            cat.remove(obj)
        args.log.info('{0} objects deleted'.format(n - len(cat)))
        return n - len(cat)


@command()
def stats(args):
    """
    cdstarcat stats

    Print summary statistics of bitstreams in the catalog to stdout.
    """
    cat = _catalog(args)
    print('Summary:')
    print('  {0:,} objects with {1:,} bitstreams of total size {2}'.format(
        len(cat), sum(len(obj.bitstreams) for obj in cat), cat.size_h))
    print('  {0} duplicate bitstreams'.format(
        sum(1 for objs in cat.md5_to_object.values() if len(objs) > 1)))
    print('  {0} objects with no bitstreams'.format(
        sum(1 for obj in cat if not obj.bitstreams)))

    print()
    types = Counter(chain(*[[bs.mimetype for bs in obj.bitstreams] for obj in cat]))
    table = Table('maintype', 'subtype', 'bitstreams')
    for maintype, items in groupby(
            sorted(types.items(), key=lambda p: (p[0].split('/')[0], -p[1])),
            lambda p: p[0].split('/')[0]):
        for k, v in items:
            table.append([maintype, k.split('/')[1], v])
    print(table.render(tablefmt='simple'))


@command()
def add(args):
    """
    cdstarcat add SPEC

    Add metadata about objects (specified by SPEC) in CDSTAR to the catalog.
    SPEC: Either a CDSTAR object ID or a query.
    """
    spec = args.args[0]
    with _catalog(args) as cat:
        n = len(cat)
        if OBJID_PATTERN.match(spec):
            cat.add_objids(spec)
        else:
            results = cat.add_query(spec)
            args.log.info('{0} hits for query {1}'.format(results, spec))
        args.log.info('{0} objects added'.format(len(cat) - n))
        return len(cat) - n


@command()
def create(args):
    """
    cdstarcat create PATH

    Create objects in CDSTAR specified by PATH.
    When PATH is a file, a single object (possibly with multiple bitstreams) is created;
    When PATH is a directory, an object will be created for each file in the directory
    (recursing into subdirectories).
    """
    with _catalog(args) as cat:
        for fname, created, obj in cat.create(args.args[0], {}):
            args.log.info('{0} -> {1} object {2.id}'.format(
                fname, 'new' if created else 'existing', obj))


@command()
def delete(args):
    """
    cdstarcat delete OID

    Delete an object specified by OID from CDSTAR.
    """
    with _catalog(args) as cat:
        n = len(cat)
        cat.delete(args.args[0])
        args.log.info('{0} objects deleted'.format(n - len(cat)))
        return n - len(cat)


@command()
def update(args):
    """
    cdstarcat update OID [KEY=VALUE]+

    Update the metadata of an object.
    """
    with _catalog(args) as cat:
        cat.update_metadata(
            args.args[0], dict([arg.split('=', 1) for arg in args.args[1:]]))


def _catalog(args):
    return Catalog(args.catalog, args.url, args.user, args.pwd)


def main():  # pragma: no cover
    parser = ArgumentParserWithLogging(__name__, stats, add, cleanup, create, delete, update)
    for arg in ['catalog', 'url', 'user', 'pwd']:
        envvar = 'CDSTAR_{0}'.format(arg.upper())
        parser.add_argument(
            '--' + arg,
            help="defaults to ${0}".format(envvar),
            default=os.environ.get(envvar))
    sys.exit(parser.main())


if __name__ == "__main__":  # pragma: no cover
    main()
