#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

""" The MSU MFSD Database for face spoofing interface. It is an extension of an
SQL-based database interface, which directly talks to the MSU MFSD database,
for verification experiments (good to use in the bob.bio.base framework). It
also implements a kind of hack so that you can run vulnerability analysis with
it. """

from bob.db.base import File as BaseFile
from bob.db.base import Database as BaseDatabase
from .query import Database as LDatabase


def selected_indices(total_number_of_indices, desired_number_of_indices=None):
    """
    Returns a list of indices that will contain exactly the number of desired
    indices (or the number of total items in the list, if this is smaller).
    These indices are selected such that they are evenly spread over the whole
    sequence.
    """

    if desired_number_of_indices is None or desired_number_of_indices >= \
       total_number_of_indices or desired_number_of_indices < 0:
        return range(total_number_of_indices)
    increase = float(total_number_of_indices) / \
        float(desired_number_of_indices)
    # generate a regular quasi-random index list
    return [int((i + .5) * increase) for i in range(desired_number_of_indices)]


class File(BaseFile):
    """msu mfsd low-level file used for vulnerability analysis in face
    recognition"""

    def __init__(self, f, framen=None):
        self._f = f
        self.framen = framen
        self.path = '{}_{:03d}'.format(f.path, framen)
        self.client_id = '{:02d}'.format(f.client_id)
        self.file_id = '{}_{}'.format(f.id, framen)
        super(File, self).__init__(path=self.path, file_id=self.file_id)

    def load(self, directory=None, extension=None):
        if extension in (None, '.mov', '.mp4'):
            # the extension is dynamic; the low-level knows about it.
            extension = None
            for i in range(100):
                try:
                    video = self._f.load(directory, extension)
                    # just return the required frame.
                    return video[self.framen]
                except RuntimeError:
                    pass
        else:
            return super(File, self).load(directory, extension)


class Database(BaseDatabase):
    """
    Implements verification API for querying msu mfsd database.
    This database loads max_number_of_frames from the video files as
    separate samples. This is different from what bob.bio.video does
    currently.
    """
    __doc__ = __doc__

    def __init__(self, max_number_of_frames=10,
                 original_directory=None, original_extension=None):
        super(Database, self).__init__(original_directory, original_extension)

        # call base class constructors to open a session to the database
        self._db = LDatabase()

        self.max_number_of_frames = max_number_of_frames or 10
        # 180 is the guaranteed number of frames in msu mfsd videos
        self.indices = selected_indices(180, self.max_number_of_frames)
        self.low_level_group_names = ('train', 'devel', 'test')
        self.high_level_group_names = ('world', 'dev', 'eval')

    def protocol_names(self):
        """Returns all registered protocol names
        Here I am going to hack and double the number of protocols
        with -licit and -spoof. This is done for running vulnerability
        analysis. The low-level interface only supports the grandtest protocol
        for now."""
        return ['grandtest-licit', 'grandtest-spoof']

    def groups(self):
        return self.convert_names_to_highlevel(
            self._db.groups(), self.low_level_group_names,
            self.high_level_group_names)

    def model_ids_with_protocol(self, groups=None, protocol=None, **kwargs):
        # since the low-level API does not support verification, we improvise.
        files = self.objects(groups=groups, protocol=protocol,
                             purposes='enroll', **kwargs)
        return sorted(set(f.client_id for f in files))

    def objects(self, groups=None, protocol=None, purposes=None,
                model_ids=None, **kwargs):
        '''Here, we do so several things to create a verification protocol:
          #. We will create a model for all clients.
          #. We will use the laptop samples for enrollment and mobile samples
             for probe.
          #. We will probe all clients against each other.'''
        protocol = self.check_parameter_for_validity(
            protocol, "protocol", self.protocol_names(), 'grandtest-licit')
        groups = self.check_parameters_for_validity(
            groups, "group", self.groups(), self.groups())
        purposes = self.check_parameters_for_validity(
            purposes, "purpose", ('enroll', 'probe'), ('enroll', 'probe'))
        purposes = list(purposes)
        groups = self.convert_names_to_lowlevel(
            groups, self.low_level_group_names, self.high_level_group_names)

        # there is only one protocol defined in the low-level db here.
        is_licit = '-licit' in protocol

        # The low-level API has only "attack", and "real"
        if len(purposes) > 1 and model_ids:
            raise NotImplementedError(
                'Currently returning both enroll and probe for specific '
                'client(s) is not supported. Please specify one purpose only.')

        # the protcol is designed here. You can see depending on the purpose
        # and protocl, different qualities and classes are selected.

        qualities = []
        classes = []
        if 'enroll' in purposes:
            qualities.append('laptop')
            classes.append('real')

        if 'probe' in purposes:
            if is_licit:
                qualities.append('mobile')
                classes.append('real')
                model_ids = None  # all models
            else:
                qualities = None  # all qualities
                classes.append('attack')

        # now, query the actual Replay database
        objects = self._db.objects(group=groups, quality=qualities,
                                   cls=classes, ids=model_ids, **kwargs)

        # make sure to return File representation of a file, not the database
        # one also make sure you replace client ids with attack
        retval = []
        for f in objects:
            for i in self.indices:
                if f.is_real():
                    retval.append(File(f, i))
                else:
                    temp = File(f, i)
                    temp.client_id = 'attack/{}'.format(f.instrument)
                    retval.append(temp)
        return retval
