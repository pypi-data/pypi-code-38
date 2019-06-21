#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#


import os
import sys
import six

from bob.pad.base.database import PadFile
from bob.pad.base.database import PadDatabase

import bob.io.base
from bob.db.base.driver import Interface as BaseInterface

import pkg_resources
data_dir = pkg_resources.resource_filename('bob.pad.base', 'test/data')

dummy_name = "spoof_test"
dummy_train_list = ['train_real', 'train_attack']
dummy_devel_list = ['dev_real', 'dev_attack']
dummy_test_list = ['eval_real', 'eval_attack']

dummy_data = {'train_real': 1.0, 'train_attack': 2.0,
              'dev_real': 3.0, 'dev_attack': 4.0,
              'eval_real': 5.0, 'eval_attack': 6.0}


class TestFile(PadFile):

    def __init__(self, path, id):
        attack_type = None
        if "attack" in path:
            attack_type = "attack"
        super(TestFile, self).__init__(client_id=1, path=path, file_id=id, attack_type=attack_type)

    def load(self, directory=None, extension='.hdf5'):
        """Loads the data at the specified location and using the given extension.
        Override it if you need to load differently.

        Keyword Parameters:

        data
          The data blob to be saved (normally a :py:class:`numpy.ndarray`).

        directory
          [optional] If not empty or None, this directory is prefixed to the final
          file destination

        extension
          [optional] The extension of the filename - this will control the type of
          output and the codec for saving the input blob.

        """
        # get the path
        path = self.make_path(directory or '', extension or '')
        return dummy_data[os.path.basename(path)]


def dumplist(args):
    """Dumps lists of files based on your criteria"""

    db = TestDatabase()
    data = db.get_all_data()
    output = sys.stdout

    if args.selftest:
        from bob.db.base.utils import null
        output = null()

    files = data[0] + data[1]
    for f in files:
        output.write('%s\n' % (f.make_path(args.directory, args.extension),))

    return 0


class Interface(BaseInterface):

    def name(self):
        return dummy_name

    def version(self):
        return '0.0.1'

    def files(self):
        return ()

    def type(self):
        return 'rawfiles'

    def add_commands(self, parser):
        from argparse import SUPPRESS

        subparsers = self.setup_parser(parser,
                                       "Dummy Spoof Database", "Dummy spoof database with attacks for testing")

        dumpparser = subparsers.add_parser('dumplist', help="")
        dumpparser.add_argument('-d', '--directory', dest="directory", default='',
                                help="if given, this path will be prepended to every entry returned "
                                     "(defaults to '%(default)s')")
        dumpparser.add_argument('-e', '--extension', dest="extension", default='',
                                help="if given, this extension will be appended to every entry returned "
                                     "(defaults to '%(default)s')")
        dumpparser.add_argument('--self-test', dest="selftest", default=False,
                                action='store_true', help=SUPPRESS)

        dumpparser.set_defaults(func=dumplist)  # action


class TestDatabase(PadDatabase):
    """ Implements API of PAD DB interface for this Test database together with some low level support methods"""

    def __init__(self, protocol='Default', original_directory=data_dir, original_extension='', **kwargs):
        # call base class constructors to open a session to the database
        super(TestDatabase, self).__init__(name='testspoof', protocol=protocol,
                                           original_directory=original_directory,
                                           original_extension=original_extension, **kwargs)

    ################################################
    # Low level support methods for the database #
    ################################################
    def create_subparser(self, subparser, entry_point_name):
        from argparse import RawDescriptionHelpFormatter

        p = subparser.add_parser(entry_point_name,
                                 help=self.short_description(),
                                 description="Dummy description",
                                 formatter_class=RawDescriptionHelpFormatter)

        p.add_argument('--dummy-test', type=str, default='test',
                       dest="kwargs_protocol",
                       help='Test the functions of subparser')

    def get_protocols(self):
        return ["test"]

    def get_attack_types(self):
        return ["attack1", "attack2"]

    def name(self):
        i = Interface()
        return "Dummy Spoof Database (%s)" % i.name()

    def short_name(self):
        i = Interface()
        return i.name()

    def version(self):
        i = Interface()
        return i.version()

    def short_description(self):
        return "Dummy spoof database with attacks for testing"

    def long_description(self):
        return "Long description"

    def implements_any_of(self, propname):
        """
        Only support for audio files is implemented/
        :param propname: The type of data-support, which is checked if it contains 'spoof'
        :return: True if propname is None, it is equal to or contains 'spoof', otherwise False.
        """
        if isinstance(propname, (tuple, list)):
            return 'spoof' in propname
        elif propname is None:
            return True
        elif isinstance(propname, six.string_types):
            return 'spoof' == propname

        # does not implement the given access protocol
        return False

    def get_all_data(self):
        return self.all_files()

    #  This is the method from PadDatabase that we must implement
    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        fileset = []
        if purposes is None or 'real' in purposes:
            if groups is None or 'train' in groups:
                fileset += [TestFile(dummy_train_list[0], 1)]
            if groups is None or 'dev' in groups:
                fileset += [TestFile(dummy_devel_list[0], 2)]
            if groups is None or 'eval' in groups:
                fileset += [TestFile(dummy_test_list[0], 3)]
        if purposes is None or 'attack' in purposes:
            if groups is None or 'train' in groups:
                fileset += [TestFile(dummy_train_list[1], 4)]
            if groups is None or 'dev' in groups:
                fileset += [TestFile(dummy_devel_list[1], 5)]
            if groups is None or 'eval' in groups:
                fileset += [TestFile(dummy_test_list[1], 6)]
        return fileset

    def annotations(self, file):
        return None


database = TestDatabase()