
"""UVAD - a mobile face presentation attack database with real-world
variations
"""

import os
import sys
import pkg_resources
from bob.db.base.driver import Interface as BaseInterface
from bob.io.base import create_directories_safe


def dumplist(args):
    """Dumps lists of files based on your criteria"""

    from .query import Database
    db = Database()

    r = db.objects(
        purposes=args.purpose,
        groups=args.group,
    )

    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    for f in r:
        output.write('%s\n' % f.make_path(
            directory=args.directory, extension=args.extension))

    return 0


def checkfiles(args):
    """Checks existence of files based on your criteria"""

    from .query import Database
    db = Database()

    r = db.objects()

    # go through all files, check if they are available on the filesystem
    good = []
    bad = []
    for f in r:
        if os.path.exists(f.make_path(args.directory, args.extension)):
            good.append(f)
        else:
            bad.append(f)

    # report
    output = sys.stdout
    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    if bad:
        for f in bad:
            output.write('Cannot find file "%s"\n' %
                         f.make_path(args.directory, args.extension))
        output.write('%d files (out of %d) were not found at "%s"\n' %
                     (len(bad), len(r), args.directory))

    return 0


def convert_filelist(outfolder, group, real_files, attack_files,
                     prepend='release_1'):
    outpaths = [
        os.path.join(outfolder, group, 'for_real.lst'),
        os.path.join(outfolder, group, 'for_attack.lst'),
    ]
    create_directories_safe(os.path.dirname(outpaths[0]))
    real_files = [os.path.join(prepend, sample) for path in real_files
                  for sample in open(path, 'rt').read().split()]
    attack_files = [os.path.join(prepend, sample) for path in attack_files
                    for sample in open(path, 'rt').read().split()]

    with open(outpaths[0], 'w') as wrf, \
            open(outpaths[1], 'w') as waf:
        for sample_path in real_files:
            wrf.write('{} {}\n'.format(sample_path, 'NA'))
        for sample_path in attack_files:
            attack_type = '/'.join(sample_path.split('/')[1:4])
            waf.write('{} {} {}\n'.format(sample_path, 'NA', attack_type))


def create(args):
    """Creates the file-lists to be used in Bob based on original file lists.
    """
    root_dir = args.root_dir
    output_dir = args.output_dir

    def create_lists(files, outfolder, root_dir):
        for group in files:
            for real in files[group]:
                files[group][real] = [os.path.join(root_dir, f)
                                      for f in files[group][real]]
        for group in files:
            convert_filelist(outfolder, group, files[group]['real'],
                             files[group]['attack'])

    # experiment 1
    files = {
        'train': {
            'real': ['real_sony_canon_kodac_train.txt'],
            'attack': [
                'attack_sony_canon_kodac_allcameras_monitors123_train.txt'],
        },
        'dev': {
            'real': ['real_nikon_olympus_panasonic_test.txt'],
            'attack': [
                'attack_nikon_olympus_panasonic_allcameras_monitors4567_test'
                '.txt'],
        },
    }
    outfolder = os.path.join(output_dir, 'experiment_1')
    create_lists(
        files, outfolder,
        os.path.join(root_dir, 'release_1/protocols/experiment_1/'))

    # experiment 2
    files = {
        'train': {
            'real': ['real_train.txt'],
            'attack': ['attack_train.txt'],
        },
        'dev': {
            'real': ['real_test.txt'],
            'attack': ['attack_test.txt'],
        },
    }
    for i in range(1, 10):
        outfolder = os.path.join(output_dir, 'experiment_2_{}'.format(i))
        create_lists(
            files, outfolder,
            os.path.join(root_dir,
                         'release_1/protocols/experiment_2/{}'.format(i)))

    # experiment 3
    mylist = zip(('1', '2'), ('123', '456'))
    for camera in ('canon', 'kodac', 'nikon', 'olympus', 'panasonic', 'sony'):
        for (ti1, ti2), (ei1, ei2) in zip(mylist, reversed(mylist)):
            files = {
                'train': {
                    'real': ['real_{}_{}.txt'.format(camera, ti1)],
                    'attack': ['attack_{}_allcameras_monitors{}.txt'.format(
                        camera, ti2)],
                },
                'dev': {
                    'real': ['real_{}_{}.txt'.format(camera, ei1)],
                    'attack': ['attack_{}_allcameras_monitors{}.txt'.format(
                        camera, ei2)],
                },
            }
            outfolder = os.path.join(
                output_dir, 'experiment_3_{}_{}'.format(camera, ti1))
            create_lists(
                files, outfolder,
                os.path.join(root_dir,
                             'release_1/protocols/experiment_3/'))


class Interface(BaseInterface):

    def name(self):
        return 'uvad'

    def version(self):
        return pkg_resources.require('bob.db.%s' % self.name())[0].version

    def files(self):
        return ()

    def type(self):
        return 'text'

    def add_commands(self, parser):

        from . import __doc__ as docs

        subparsers = self.setup_parser(parser,
                                       "UVAD database", docs)

        import argparse

        # the "dumplist" action
        parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
        parser.add_argument(
            '-d', '--directory', default='',
            help="if given, this path will be prepended to every entry "
            "returned.")
        parser.add_argument(
            '-e', '--extension', default='',
            help="if given, this extension will be appended to every entry "
            "returned.")
        parser.add_argument(
            '-u', '--purpose', help="if given, this value will limit the "
            "output files to those designed for the given purposes.",
            choices=('enroll', 'probe', ''))
        parser.add_argument(
            '-g', '--group',
            help="if given, this value will limit the output files to those "
            "belonging to a particular protocolar group.",
            choices=('dev', 'eval', 'world', ''))
        parser.add_argument('--self-test', dest="selftest",
                            action='store_true', help=argparse.SUPPRESS)
        parser.set_defaults(func=dumplist)  # action

        # the "checkfiles" action
        parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
        parser.add_argument(
            '-l', '--list-directory', required=True,
            help="The directory which contains the file lists.")
        parser.add_argument(
            '-d', '--directory', dest="directory", default='',
            help="if given, this path will be prepended to every entry "
            "returned.")
        parser.add_argument(
            '-e', '--extension', dest="extension", default='',
            help="if given, this extension will be appended to every entry "
            "returned.")
        parser.add_argument('--self-test', dest="selftest",
                            action='store_true', help=argparse.SUPPRESS)
        parser.set_defaults(func=checkfiles)  # action

        # the "create" action
        parser = subparsers.add_parser('create', help=create.__doc__)
        parser.add_argument(
            '-d', '--root-dir',
            help='The directory where the original database is.')
        default_output = pkg_resources.resource_filename(__name__, 'lists')
        parser.add_argument(
            '-o', '--output-dir', default=default_output,
            help='The directory where the new list files will be saved into.')
        parser.set_defaults(func=create)  # action
