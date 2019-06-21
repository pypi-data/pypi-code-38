#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""   The Replay-Mobile Database for face spoofing implementation of
bob.bio.base.database.BioDatabase interface."""

from .database import VideoBioFile
from bob.bio.base.database import BioDatabase
from bob.extension import rc
from bob.bio.video import FrameSelector


class ReplayMobileVideoBioFile(VideoBioFile):
    """VideoBioFile implementation of the Replay Mobile Database"""

    def __init__(self, f):
        super(ReplayMobileVideoBioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self._f = f

    def load(self, directory=None, extension='.mov',
             frame_selector=FrameSelector(selection_style='all')):
        vid = self._f.load(directory=directory, extension=extension)
        return frame_selector(vid)

    @property
    def annotations(self):
        return self._f.annotations

    @property
    def frames(self):
        return self._f.frames

    @property
    def number_of_frames(self):
        return self._f.number_of_frames

    @property
    def frame_shape(self):
        return self._f.frame_shape


class ReplayMobileVideoBioDatabase(BioDatabase):
    """
    ReplayMobile database implementation of :py:class:`bob.bio.base.database.BioDatabase` interface.
    It is an extension of an SQL-based database interface, which directly talks to ReplayMobile database, for
    verification experiments (good to use in bob.bio.base framework).
    """

    def __init__(self,
                 original_directory=rc['bob.db.replaymobile.directory'],
                 original_extension='.mov',
                 annotation_directory=None,
                 annotation_extension='.json',
                 annotation_type='json',
                 **kwargs):
        from bob.db.replaymobile import Database as LowLevelDatabase
        self._db = LowLevelDatabase(
            original_directory=original_directory,
            original_extension=original_extension,
            annotation_directory=annotation_directory,
            annotation_extension=annotation_extension,
            annotation_type=annotation_type,
        )

        # Since the high level API expects different group names than what the
        # low level API offers, you need to convert them when necessary
        self.low_level_group_names = (
            'train', 'devel',
            'test')  # group names in the low-level database interface
        self.high_level_group_names = (
            'world', 'dev',
            'eval')  # names are expected to be like that in objects() function

        # call base class constructors to open a session to the database
        super(ReplayMobileVideoBioDatabase, self).__init__(
            name='replaymobile',
            original_directory=original_directory,
            original_extension=original_extension,
            annotation_directory=annotation_directory,
            annotation_extension=annotation_extension,
            annotation_type=annotation_type,
            **kwargs)

    @property
    def original_directory(self):
        return self._db.original_directory

    @original_directory.setter
    def original_directory(self, value):
        self._db.original_directory = value

    @property
    def original_extension(self):
        return self._db.original_extension

    @original_extension.setter
    def original_extension(self, value):
        self._db.original_extension = value

    @property
    def annotation_directory(self):
        return self._db.annotation_directory

    @annotation_directory.setter
    def annotation_directory(self, value):
        self._db.annotation_directory = value

    @property
    def annotation_extension(self):
        return self._db.annotation_extension

    @annotation_extension.setter
    def annotation_extension(self, value):
        self._db.annotation_extension = value

    @property
    def annotation_type(self):
        return self._db.annotation_type

    @annotation_type.setter
    def annotation_type(self, value):
        self._db.annotation_type = value

    def protocol_names(self):
        """Returns all registered protocol names
        Here I am going to hack and double the number of protocols
        with -licit and -spoof. This is done for running vulnerability
        analysis"""
        names = [p.name + '-licit' for p in self._db.protocols()]
        names += [p.name + '-spoof' for p in self._db.protocols()]
        return names

    def groups(self):
        return self.high_level_group_names

    def model_ids_with_protocol(self, groups=None, protocol=None, **kwargs):
        # since the low-level API does not support verification
        # straight-forward-ly, we improvise.
        files = self._db.objects(groups=groups, protocol=protocol,
                                 cls='enroll', **kwargs)
        return sorted(set(f.client_id for f in files))

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        if protocol == '.':
            protocol = None
        protocol = self.check_parameter_for_validity(
            protocol, "protocol", self.protocol_names(), 'grandtest-licit')
        groups = self.check_parameters_for_validity(
            groups, "group", self.groups(), self.groups())
        purposes = self.check_parameters_for_validity(
            purposes, "purpose", ('enroll', 'probe'), ('enroll', 'probe'))
        purposes = list(purposes)
        groups = self.convert_names_to_lowlevel(
            groups, self.low_level_group_names, self.high_level_group_names)

        # protocol licit is not defined in the low level API
        # so do a hack here.
        if '-licit' in protocol:
            # for licit we return the grandtest protocol
            protocol = protocol.replace('-licit', '')
            # The low-level API has only "attack", "real", "enroll" and "probe"
            # should translate to "real" or "attack" depending on the protocol.
            # enroll does not to change.
            if 'probe' in purposes:
                purposes.remove('probe')
                purposes.append('real')
                if len(purposes) == 1:
                    # making the model_ids to None will return all clients
                    # which make the impostor data also available.
                    model_ids = None
                elif model_ids:
                    raise NotImplementedError(
                        'Currently returning both enroll and probe for '
                        'specific client(s) in the licit protocol is not '
                        'supported. Please specify one purpose only.')

        elif '-spoof' in protocol:
            protocol = protocol.replace('-spoof', '')
            # you need to replace probe with attack and real for the spoof
            # protocols. You can add the real here also to create positives
            # scores also but usually you get these scores when you run the
            # licit protocol
            if 'probe' in purposes:
                purposes.remove('probe')
                purposes.append('attack')

        # now, query the actual Replay database
        objects = self._db.objects(
            groups=groups, protocol=protocol, cls=purposes, clients=model_ids,
            **kwargs)

        # make sure to return File representation of a file, not the database
        # one also make sure you replace client ids with attack
        retval = []
        for f in objects:
            if f.is_real():
                retval.append(ReplayMobileVideoBioFile(f))
            else:
                temp = ReplayMobileVideoBioFile(f)
                attack = f.get_attack()
                temp.client_id = 'attack/{}'.format(
                    attack.attack_device, attack.attack_support)
                retval.append(temp)
        for f in retval:
            f.original_directory = self.original_directory
        return retval

    def arrange_by_client(self, files):
        client_files = {}
        for file in files:
            if str(file.client_id) not in client_files:
                client_files[str(file.client_id)] = []
            client_files[str(file.client_id)].append(file)

        files_by_clients = []
        for client in sorted(client_files.keys()):
            files_by_clients.append(client_files[client])
        return files_by_clients

    def annotations(self, file):
        return file.annotations
