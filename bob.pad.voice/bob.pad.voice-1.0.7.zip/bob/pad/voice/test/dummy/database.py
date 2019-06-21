#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 17 May 15:43:22 CEST 2016

import sys

import bob.pad.base.database
import bob.io.base

from bob.pad.voice.database import PadVoiceFile

from bob.io.base.test_utils import datafile
from bob.db.base.driver import Interface as BaseInterface

import pkg_resources

data_dir = pkg_resources.resource_filename('bob.pad.voice', 'test/data')

dummy_name = "speech_spoof_test"


def F(f):
    """Returns the test file on the "data" subdirectory"""
    return datafile(f, __name__)


class TestFile(PadVoiceFile):
    def __init__(self, path, file_id):
        attacktype = None
        if "attack" in path:
            attacktype = 'attack'
        super(TestFile, self).__init__(client_id=1, path=path, file_id=file_id, attack_type=attacktype)



def dumplist(args):
    """Dumps lists of files based on your criteria"""

    db = DummyDatabaseSpeechSpoof()

    data = db.all_files()

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
        # from pkg_resources import resource_filename
        # raw_files = ('*.wav',)
        # return [resource_filename(__name__, k) for k in raw_files]
        return ()

    def type(self):
        return 'rawfiles'

    def add_commands(self, parser):
        from argparse import SUPPRESS

        subparsers = self.setup_parser(parser,
                                       "Dummy Speech Database", "Dummy speech database with attacks for testing")

        dumpparser = subparsers.add_parser('dumplist', help="")
        dumpparser.add_argument('-d', '--directory', dest="directory", default='',
                                help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
        dumpparser.add_argument('-e', '--extension', dest="extension", default='.wav',
                                help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
        dumpparser.add_argument('--self-test', dest="selftest", default=False,
                                action='store_true', help=SUPPRESS)

        dumpparser.set_defaults(func=dumplist)  # action


class DummyDatabaseSpeechSpoof(bob.pad.base.database.PadDatabase):
    """ Implements API of antispoofing interface for this Test database"""

    def __init__(self, protocol='Default', original_directory=data_dir, original_extension=".wav", **kwargs):
        # call base class constructors to open a session to the database
        bob.pad.base.database.PadDatabase.__init__(self, name='testspeech', protocol=protocol,
                                                 original_directory=original_directory,
                                                 original_extension=original_extension, **kwargs)

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        """Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        groups
            One of the groups ('dev', 'eval', 'train') or a tuple with several of them.
            If 'None' is given (this is the default), it is considered the same as a
            tuple with all possible values.

        protocol
          The protocol for which the clients should be retrieved.
          The protocol is dependent on your database.
          If you do not have protocols defined, just ignore this field.

        purposes
            The purposes can be either 'real' or 'attack'.

        model_ids
            This parameter is not supported in this implementation.


        Returns: A set of Files with the specified properties.
        """

        return_list = []
        if 'real' in purposes:
            if 'train' in groups:
                return_list.append(TestFile("genuine_laptop_sentence01", 1))
            if 'dev' in groups:
                return_list.append(TestFile("genuine_laptop2_sentence01", 3))
            if 'eval' in groups:
                return_list.append(TestFile("genuine_phone_sentence01", 5))
        if 'attack' in purposes:
            if 'train' in groups:
                return_list.append(TestFile("attack_laptop_sentence01", 2))
            if 'dev' in groups:
                return_list.append(TestFile("attack_phone_sentence01", 4))
            if 'eval' in groups:
                return_list.append(TestFile("attack_ss_sentence01", 6))

        return return_list

    def annotations(self, file):
        pass

database = DummyDatabaseSpeechSpoof(
    protocol='Default',
    original_directory=data_dir,
    original_extension=".wav",
    training_depends_on_protocol=True,
)
