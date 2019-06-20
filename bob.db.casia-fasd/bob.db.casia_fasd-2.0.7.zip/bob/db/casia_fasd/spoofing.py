#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""CASIA Face-AntiSpoofing Database (FASD) implementation"""

import os
import six
from . import __doc__ as long_description
from . import File as CasiaFASDFile, Database as CasiaFASDDatabase


class File(object):
    def __init__(self, f):
        """Initializes this File object with the bob.db.casia_fasd.File equivalent"""
        self.__f = f

    def videofile(self, directory=None):
        return self.__f.videofile(directory=directory)

    videofile.__doc__ = FileBase.videofile.__doc__

    def facefile(self, directory=None):

        if directory != None:
            directory = os.path.join(directory, 'face-locations')
        return self.__f.facefile(directory=directory)

    facefile.__doc__ = FileBase.facefile.__doc__

    def bbx(self, directory=None):
        return self.__f.bbx(directory=directory)

    bbx.__doc__ = FileBase.bbx.__doc__

    def load(self, directory=None, extension='.hdf5'):
        return self.__f.load(directory=directory, extension=extension)

    load.__doc__ = FileBase.bbx.__doc__

    def save(self, data, directory=None, extension='.hdf5'):
        return self.__f.save(data, directory=directory, extension=extension)

    save.__doc__ = FileBase.save.__doc__

    def make_path(self, directory=None, extension=None):
        return self.__f.make_path(directory=directory, extension=extension)

    make_path.__doc__ = FileBase.make_path.__doc__

    def get_client_id(self):
        return self.__f.get_clientid()

    get_client_id.__doc__ = FileBase.get_client_id.__doc__

    def is_real(self):
        return self.__f.is_real()

    is_real.__doc__ = FileBase.is_real.__doc__

    def get_type(self):
        return self.__f.get_type()

    get_type.__doc__ = "Returns the type of attack for this sample"

    def get_quality(self):
        return self.__f.get_quality()

    get_quality.__doc__ = "Returns the quality of attack for this sample"


class Database(object):
    __doc__ = long_description

    def __init__(self, args=None):
        if args is not None:
            self.__db = CasiaFASDDatabase(args.foldsdir)
        else:
            self.__db = CasiaFASDDatabase()
        self.__kwargs = {}
        if args is not None:

            self.__kwargs = {
                'types': args.casia_types,
                'qualities': args.casia_qualities,
                'fold_no': args.casia_fold_number,
            }

    __init__.__doc__ = DatabaseBase.__init__.__doc__

    def set_foldsdir(self, foldsdir):
        """Sets the directory holding the cross validation protocol"""
        self.__db.set_foldsdir(foldsdir)

    def get_protocols(self):
        # In the case of this DB, this method does not precisely return the protocols (there are None defined actually!)
        return list(self.__db.types)

    def get_attack_types(self):
        return list(self.__db.types)

    def create_subparser(self, subparser, entry_point_name):

        from argparse import RawDescriptionHelpFormatter

        ## remove '.. ' lines from rst
        desc = '\n'.join([
            k for k in self.long_description().split('\n')
            if k.strip().find('.. ') != 0
        ])

        p = subparser.add_parser(
            entry_point_name,
            help=self.short_description(),
            description=desc,
            formatter_class=RawDescriptionHelpFormatter)

        p.add_argument(
            '--types',
            type=str,
            choices=self.__db.types,
            dest='casia_types',
            nargs='+',
            help=
            'Defines the types of attack videos in the database that are going to be used (if not set return all types)'
        )

        p.add_argument(
            '--qualities',
            type=str,
            choices=self.__db.qualities,
            dest='casia_qualities',
            help=
            'Defines the qualities of attack videos in the database that are going to be used (if not set return all qualities)'
        )

        p.add_argument(
            '--fold-number',
            choices=(1, 2, 3, 4, 5),
            type=int,
            default=1,
            dest='casia_fold_number',
            help='Number of the fold (defaults to %(default)s)')

        p.add_argument(
            '--foldsdir',
            type=str,
            dest='foldsdir',
            help=
            'The directory where the cross-validation protocol files are stored. An absolute path needs to be provided. If not specified, the default cross-validation files are used'
        )

        p.set_defaults(name=entry_point_name)
        p.set_defaults(cls=Database)

        return

    create_subparser.__doc__ = DatabaseBase.create_subparser.__doc__

    def name(self):
        from .driver import Interface
        i = Interface()
        return "CASIA FASD database (%s)" % i.name()

    def short_name(self):
        from .driver import Interface
        i = Interface()
        return i.name()

    def version(self):
        from .driver import Interface
        i = Interface()
        return i.version()

    def short_description(self):
        return 'CASIA Face Anti-Spoofing database (FASD)'

    short_description.__doc__ = DatabaseBase.short_description.__doc__

    def long_description(self):
        return Database.__doc__

    long_description.__doc__ = DatabaseBase.long_description.__doc__

    def implements_any_of(self, propname):
        if isinstance(propname, (tuple, list)):
            return 'video' in propname
        elif propname is None:
            return True
        elif isinstance(propname, six.string_types):
            return 'video' == propname

        # does not implement the given access protocol
        return False

    def __parse_arguments(self):

        types = self.__kwargs.get('types', self.__db.types)
        qualities = self.__kwargs.get('qualities', self.__db.qualities)
        if not types: types = self.__db.types
        return types, qualities, self.__kwargs.get('fold_no', 1)

    def get_clients(self, group=None):
        if group == 'train':
            objects = self.get_train_data(
            )[0]  # only the real access objects are enough to query the client ids
        elif group == 'devel':
            objects = self.get_devel_data()[0]
        elif group == 'test':
            objects = self.get_test_data()[0]
        else:
            objects = self.get_train_data()[0] + self.get_devel_data(
            )[0] + self.get_test_data()[0]

        return list(set([obj.get_client_id() for obj in objects]))

    def get_enroll_data(self, group=None, fold_no=0, enroll_quality='high'):
        __doc__ = DatabaseBase.get_enroll_data.__doc__
        """Returns enrollment objects for a specific group"""
        # enroll_quality is a parameter stating which kind of videos will be used for enrollment

        if group == 'train':
            _, retval = self.__db.cross_valid_foldobjects(
                cls='real', fold_no=fold_no, qualities=enroll_quality)
        elif group == 'devel':
            retval, _ = self.__db.cross_valid_foldobjects(
                cls='real', fold_no=fold_no, qualities=enroll_quality)
        elif group == 'test':
            retval = self.__db.objects(
                groups='test', cls='real', qualities=enroll_quality)

        return retval  #raise RuntimeError("This dataset does not have enrollment data")

    get_enroll_data.__doc__ = DatabaseBase.get_enroll_data.__doc__

    def get_train_data(self, fold_no=0, enroll_quality=None):
        __doc__ = DatabaseBase.get_train_data.__doc__
        # enroll_quality is a parameter stating which kind of videos will be used for enrollment. If not None, then this enrollment quality will be exempted from the rest of the qualities used in this method. If None, then the method assumes that no enrollment samples are used and all the qualities are valid as non-enrollment ones.
        if fold_no == 0:
            types, qualities, fold_no = self.__parse_arguments()
        else:
            types, qualities, _ = self.__parse_arguments()

        _, trainAttack = self.__db.cross_valid_foldobjects(
            cls='attack', types=types, fold_no=fold_no, qualities=qualities
        )  # enrollment quality does not play a role when probing attacks

        if enroll_quality != None:  # this means that the enrollment_quality is exempted from the returned real samples
            qualities = list(set(qualities) - set(enroll_quality))
        _, trainReal = self.__db.cross_valid_foldobjects(
            cls='real', fold_no=fold_no, qualities=qualities)

        return [File(f) for f in trainReal], [File(f) for f in trainAttack]

    get_train_data.__doc__ = DatabaseBase.get_train_data.__doc__

    def get_devel_data(self, fold_no=0, enroll_quality=None):
        __doc__ = DatabaseBase.get_devel_data.__doc__

        # enroll_quality is a parameter stating which kind of videos will be used for enrollment. If not None, then this enrollment quality will be exempted from the rest of the qualities used in this method. If None, then the method assumes that no enrollment samples are used and all the qualities are valid as non-enrollment ones.

        if fold_no == 0:
            types, qualities, fold_no = self.__parse_arguments()
        else:
            types, qualities, _ = self.__parse_arguments()

        develAttack, _ = self.__db.cross_valid_foldobjects(
            cls='attack', types=types, fold_no=fold_no, qualities=qualities
        )  # enrollment quality does not play a role when probing attacks

        if enroll_quality != None:  # this means that the enrollment_quality is exempted from the returned real samples
            qualities = list(set(qualities) - set(enroll_quality))
        develReal, _ = self.__db.cross_valid_foldobjects(
            cls='real', fold_no=fold_no, qualities=qualities)

        return [File(f) for f in develReal], [File(f) for f in develAttack]

    get_devel_data.__doc__ = DatabaseBase.get_devel_data.__doc__

    def get_test_data(self, fold_no=0, enroll_quality=None):
        __doc__ = DatabaseBase.get_test_data.__doc__

        # enroll_quality is a parameter stating which kind of videos will be used for enrollment. If not None, then this enrollment quality will be exempted from the rest of the qualities used in this method. If None, then the method assumes that no enrollment samples are used and all the qualities are valid as non-enrollment ones.
        if fold_no == 0:
            types, qualities, fold_no = self.__parse_arguments()
        else:
            types, qualities, _ = self.__parse_arguments()

        testAttack = self.__db.objects(
            groups='test', cls='attack', types=types, qualities=qualities
        )  # enrollment quality does not play a role when probing attacks

        if enroll_quality != None:  # this means that the enrollment_quality is exempted from the returned real samples
            qualities = list(set(qualities) - set(enroll_quality))
        testReal = self.__db.objects(
            groups='test', cls='real', qualities=qualities)

        return [File(f) for f in testReal], [File(f) for f in testAttack]

    get_test_data.__doc__ = DatabaseBase.get_test_data.__doc__

    def get_test_filters(self):
        return ('types', 'qualities')
        #raise NotImplementedError("Test filters have not yet been implemented for this database")

    def get_filtered_test_data(self, filter, fold_no=0):
        real, attack = self.get_test_data(fold_no=fold_no)

        if filter == 'types':
            return {
                'warped': (real,
                           [k for k in attack if k.get_type() == 'warped']),
                'cut': (real, [k for k in attack if k.get_type() == 'cut']),
                'video': (real,
                          [k for k in attack if k.get_type() == 'video']),
            }
        elif filter == 'qualities':
            return {
                'low': ([k for k in real if k.get_quality() == 'low'],
                        [k for k in attack if k.get_quality() == 'low']),
                'normal': ([k for k in real if k.get_quality() == 'normal'],
                           [k for k in attack if k.get_quality() == 'normal']),
                'high': ([k for k in real if k.get_quality() == 'high'],
                         [k for k in attack if k.get_quality() == 'high']),
            }

    def get_filtered_devel_data(self, filter, fold_no=0):
        real, attack = self.get_devel_data(fold_no=fold_no)

        if filter == 'types':
            return {
                'warped': (real,
                           [k for k in attack if k.get_type() == 'warped']),
                'cut': (real, [k for k in attack if k.get_type() == 'cut']),
                'video': (real,
                          [k for k in attack if k.get_type() == 'video']),
            }
        elif filter == 'qualities':
            return {
                'low': ([k for k in real if k.get_quality() == 'low'],
                        [k for k in attack if k.get_quality() == 'low']),
                'normal': ([k for k in real if k.get_quality() == 'normal'],
                           [k for k in attack if k.get_quality() == 'normal']),
                'high': ([k for k in real if k.get_quality() == 'high'],
                         [k for k in attack if k.get_quality() == 'high']),
            }

    def get_all_data(self):
        __doc__ = DatabaseBase.get_all_data.__doc__

        types, qualities, _ = self.__parse_arguments()

        allReal = self.__db.objects(cls='real', qualities=qualities)
        allAttacks = self.__db.objects(
            cls='attack', types=types, qualities=qualities)

        return [File(f) for f in allReal], [File(f) for f in allAttacks]

    get_all_data.__doc__ = DatabaseBase.get_all_data.__doc__
