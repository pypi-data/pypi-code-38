#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""Commands the AT&T database can respond to.
"""

import os
import sys
import pkg_resources
from bob.db.base.driver import Interface as BaseInterface


def dumplist(args):
  """Dumps lists of files based on your criteria."""

  from .__init__ import Database
  db = Database()

  r = db.objects(
      groups=args.group,
      purposes=args.purpose,
      model_ids=args.client
  )

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % f.make_path(directory=args.directory, extension=args.extension))

  return 0


def checkfiles(args):
  """Checks the existence of the files based on your criteria."""

  from . import Database
  db = Database()

  # go through all files, check if they are available
  bad = [f for f in db.objects() if not os.path.exists(f.make_path(directory=args.directory, extension=args.extension))]

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for f in bad:
      output.write('Cannot find file "%s"\n' % f.make_path(directory=args.directory, extension=args.extension))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(db.objects()), args.directory))

  return 0


def reverse(args):
  """Returns a list of file database identifiers given the path stems"""

  from .query import Database
  db = Database()

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  r = db.reverse(args.path)
  for f in r: output.write('%s\n' % f.id)

  if not r: return 1

  return 0


def path(args):
  """Returns a list of fully formed paths or stems given some file id"""

  from .query import Database
  db = Database()

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  r = db.paths(args.id, prefix=args.directory, suffix=args.extension)
  for path in r: output.write('%s\n' % path)

  if not r: return 1

  return 0


def download(arguments):
  """Downloads and uncompresses the AT&T database"""

  """
  Parameters:

    arguments (argparse.Namespace): A set of arguments passed by the
      command-line parser


  Returns:

    int: A POSIX compliant return value of ``0`` if the download is successful,
    or ``1`` in case it is not.


  Raises:

    urllib2.HTTPError: if the target resource does not exist on the webserver

  """

  source_url = 'http://www.cl.cam.ac.uk/research/dtg/attarchive/pub/data/att_faces.zip'

  import tempfile
  import zipfile
  if sys.version_info[0] <= 2:
    import urllib2 as urllib
  else:
    import urllib.request as urllib

  if not arguments.quiet:
    print ("Extracting url `%s' into `%s'" %(source_url, arguments.output_dir))
  u = urllib.urlopen(source_url)
  f = tempfile.NamedTemporaryFile(suffix = ".zip")
  open(f.name, 'wb').write(u.read())
  z = zipfile.ZipFile(f, mode='r')
  members = z.infolist()
  for k,m in enumerate(members):
    if not arguments.quiet:
      print("x [%d/%d] %s" % (k+1, len(members), m.filename,))
    z.extract(m, arguments.output_dir)
  z.close()
  f.close()

  return 0


class Interface(BaseInterface):

  def name(self):
    return 'atnt'

  def version(self):
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def files(self):
    return ()

  def type(self):
    return 'python_integrated'

  def add_commands(self, parser):

    from . import __doc__ as docs

    subparsers = self.setup_parser(parser,
        "AT&T/ORL Face database", docs)

    from . import Database
    from .models import Client
    import argparse

    db = Database()

    # add the dumplist command
    dump_parser = subparsers.add_parser('dumplist', help="Dumps list of files based on your criteria")
    dump_parser.add_argument('-d', '--directory', default='', help="if given, this path will be prepended to every entry returned.")
    dump_parser.add_argument('-e', '--extension', default='', help="if given, this extension will be appended to every entry returned.")
    dump_parser.add_argument('-C', '--client', type=int, help="if given, limits the dump to a particular client.", choices=Client.m_valid_client_ids)
    dump_parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group.", choices=db.m_groups)
    dump_parser.add_argument('-p', '--purpose', help="if given, this value will limit the output files to those belonging to a particular purpose.", choices=db.m_purposes)
    dump_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    from .models import DEFAULT_DATADIR
    check_parser = subparsers.add_parser('checkfiles', help="Check if the files exist, based on your criteria")
    check_parser.add_argument('-d', '--directory', default=DEFAULT_DATADIR, help="the path to the AT&T images [default: %(default)s]")
    check_parser.add_argument('-e', '--extension', default=".pgm", help="the extension of the AT&T images [default: %(default)s]")
    check_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action

    # adds the "reverse" command
    parser = subparsers.add_parser('reverse', help=reverse.__doc__)
    parser.add_argument('path', nargs='+', help="one or more path stems to look up. If you provide more than one, files which cannot be reversed will be omitted from the output.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=reverse) #action

    # adds the "path" command
    parser = subparsers.add_parser('path', help=path.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('id', type=int, nargs='+', help="one or more file ids to look up. If you provide more than one, files which cannot be found will be omitted from the output. If you provide a single id to lookup, an error message will be printed if the id does not exist in the database. The exit status will be non-zero in such case.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=path) #action

    # adds the "download" command
    parser = subparsers.add_parser('download', help=download.__doc__)
    parser.add_argument('-o', "--output-dir", help='the directory where to extract the AT&T database at [default: %(default)s]', default=DEFAULT_DATADIR)
    parser.add_argument('-q', "--quiet", action='store_true', help='if set, do it quietly', default=False)
    parser.set_defaults(func=download)
