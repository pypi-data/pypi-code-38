"""
Implementation of high-level interfaces for FileList-based databases that can be
used by both verification and PAD experiments.
"""

from bob.pad.base.database import PadFile
from bob.pad.base.database import FileListPadDatabase

from bob.bio.base.database import FileListBioDatabase
from bob.bio.base.database.file import BioFile

import bob.io.base

import numpy
import scipy


class HighPadFile(PadFile):
    """
    A simple base class that defines basic properties of File object for the use in PAD experiments.
    Replace this class for the specific database.
    """

    def __init__(self, client_id, path, attack_type=None, file_id=None):
        """**Constructor Documentation**

        Initialize the Voice File object that can read WAV files.

        Parameters:

        For client_id, path, attack_type, and file_id, please refer
        to :py:class:`bob.pad.base.database.PadFile` constructor

        """

        super(HighPadFile, self).__init__(client_id, path, attack_type, file_id)

    def load(self, directory=None, extension='.wav'):
        path = self.make_path(directory, extension)
        # read audio
        if extension == '.wav':
            rate, audio = scipy.io.wavfile.read(path)
            # We consider there is only 1 channel in the audio file => data[0]
            return rate, numpy.cast['float'](audio)
        elif extension == '.avi':
            return bob.io.base.load(path)


class HighPadDatabase(FileListPadDatabase):
    def __init__(self,
                 filelists_directory=None,
                 original_directory="[DB_DATA_DIRECTORY]",
                 original_extension=".wav",
                 file_class=None,
                 db_name='',
                 **kwargs):
        if not filelists_directory:
            # if not provided, we assume the lists are located in '../lists'
            from pkg_resources import resource_filename
            filelists_directory = resource_filename(__name__, '../lists/' + db_name)
        if not file_class:
            file_class = HighPadFile
        super(HighPadDatabase, self).__init__(filelists_directory, db_name, pad_file_class=file_class,
                                              original_directory=original_directory,
                                              original_extension=original_extension,
                                              **kwargs)


class HighBioDatabase(FileListBioDatabase):
    """
    Implements verification API for querying High database.
    """

    def __init__(self,
                 filelists_directory=None,
                 original_directory="[DB_DATA_DIRECTORY]",
                 original_extension=".wav",
                 db_name='',
                 file_class=None,
                 **kwargs):
        if not filelists_directory:
            # if not provided, we assume the lists are located in '../lists'
            from pkg_resources import resource_filename
            filelists_directory = resource_filename(__name__, '../lists/' + db_name)
        if not file_class:
            file_class = HighPadFile
        # call base class constructors to open a session to the database
        super(HighBioDatabase, self).__init__(filelists_directory, db_name,
                                              bio_file_class=file_class,
                                              original_directory=original_directory,
                                              original_extension=original_extension, **kwargs)

        self._pad_db = HighPadDatabase(filelists_directory=filelists_directory,
                                        db_name=db_name,
                                        file_class=file_class,
                                        original_directory=original_directory,
                                        original_extension=original_extension,
                                        **kwargs)

        self.low_level_group_names = ('train', 'dev', 'eval')
        self.high_level_group_names = ('world', 'dev', 'eval')

    def _convert_protocol(self, protocol=None):
        """
        This conversion of the protocol with appended '-licit' or '-spoof' is a hack for verification experiments.
        To adapt spoofing databases to the verification experiments, we need to be able to split a given protocol
        into two parts: when data for licit (only real/genuine data is used) and data for spoof
        (attacks are used instead of real data) is used in the experiment.
        Hence, we use this trick with appending '-licit' or '-spoof' to the
        protocol name, so we can distinguish these two scenarios.
        By default, if nothing is appended, we assume licit protocol.
        The distinction between licit and spoof is expressed via purposes parameters, but
        the difference is in the terminology only.
        """

        if protocol == '.':
            protocol = None

        # if protocol was empty, we return None
        if not protocol:
            return None, None

        # lets check if we have an appendix to the protocol name
        modifier = None
        if protocol:
            modifier = protocol.split('-')[-1]

        # if protocol was empty or there was no correct appendix, we just assume the 'licit' option
        if not (modifier == 'licit' or modifier == 'spoof'):
            modifier = 'licit'
        else:
            # put back everything except the appendix into the protocol
            protocol = '-'.join(protocol.split('-')[:-1])

        return protocol, modifier

    def _convert_purposes(self, purposes, modifier):
        """
        We assume there is no enrollment data, since
        PAD File database has real and attack lists only,
        so we cannot assume any availability of enrollment data
        If your PAD File lists also have for_model.lst
        and/or for_probe.lst files, you need to change this method

        Args:
            purposes: The original purposes supplied by Bio verification framework
            modifier: Indicates whether it is licit or spoof scenario

        Returns: corrected purposes according to either licit or spoof scenarios

        """

        if isinstance(purposes, str):
            purposes = [purposes]
        elif purposes is not None:
            purposes = list(purposes)

        # licit scenario considers genuine data only
        # we return all real data
        purposes = ['real']

        # spoof scenario uses spoofed data for probe
        # but, during scoring, this scenario also needs a real-probe data
        # for cases when model_id is equal to client_id
        # Hence, we request both real and attack data
        if modifier == 'spoof':
            # we return real and attack data
            purposes.append('attack')

        return purposes

    def _filter_by_model_ids(self, objects, model_ids):
        """
        From all File objects, keep only those, whose client_id is in model_ids
        Args:
            objects: File objects derived from BioFile
            model_ids: The list of the requested model Ids

        Returns: The list of File objects

        """
        if not model_ids:
            return []

        filtered_objects = []
        for f in objects:
            if f.client_id in model_ids:
                if hasattr(f, 'attack_type') and f.attack_type is not None:
                    f.client_id = 'attack/{}'.format(f.client_id)
                filtered_objects.append(f)
        return filtered_objects

    def client_id_from_model_id(self, model_id, group='dev'):
        """
        This wrapper around PAD database does not have a knowledge of
        model ids used in verification experiments, so we just assume that
        the client_id is the same as model_id, which is actually true
        for most of the verification databases as well.
        """
        return model_id

    def model_ids_with_protocol(self, groups=None, protocol=None, **kwargs):
        """
        This wrapper around PAD database does not have a knowledge of
        model ids used in verification experiments, so we just assume that
        the model_ids are the same as client ids, which is actually true
        for most of the verification databases as well.

        """
        # we need to correctly convert groups first
        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)
        # we also need to convert protocol name (it can have either '-licit' or '-spoof' appendix)
        # to the expected protocol name without appendix
        return self._pad_db.client_ids(protocol=self._convert_protocol(protocol)[0], groups=groups, **kwargs)

    def arrange_by_client(self, files):
        client_files = {}
        for f in files:
            if str(f.client_id) not in client_files:
                client_files[str(f.client_id)] = []
            client_files[str(f.client_id)].append(f)

        files_by_clients = []
        for client in sorted(client_files.keys()):
            files_by_clients.append(client_files[client])
        return files_by_clients

    def objects(self, protocol=None, purposes=None, model_ids=None, groups=None, **kwargs):
        """
        Maps objects method of PAD databases into objects method of
        Verification database

        Parameters
        ----------
        protocol : str
            To distinguish two vulnerability scenarios, protocol name should
            have either '-licit' or '-spoof' appended to it. For instance, if
            DB has protocol 'general', the named passed to this method should
            be 'general-licit', if we want to run verification experiments on
            bona fide data only, but it should be 'general-spoof', if we want
            to run it for spoof scenario (the probes are attacks).
        purposes : [str]
            This parameter is passed by the ``bob.bio.base`` verification
            experiment
        model_ids : [object]
            This parameter is passed by the ``bob.bio.base`` verification
            experiment
        groups : [str]
            We map the groups from ('world', 'dev', 'eval') used in
            verification experiments to ('train', 'dev', 'eval')
        **kwargs
            The rest of the parameters valid for a given database

        Returns
        -------
        [object]
            Set of BioFiles that verification experiments expect.

        """
        # convert group names from the conventional names in verification experiments to the internal database names
        if groups is None:  # all groups are assumed
            groups = self.high_level_group_names
        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)

        protocol, modifier = self._convert_protocol(protocol)
        purposes = self._convert_purposes(purposes, modifier)

        # Query the underline PAD database
        objects = self._pad_db.objects(protocol=protocol, groups=groups, purposes=purposes, **kwargs)

        # note that PAD database does not know anything about model_ids, so these are ignored
        # Hence, for the spoofing protocol, we need to filter out the files and
        # keep only those that belong to model_ids
        # We also modify the client_id to reflect that it is an attack
        if modifier == 'spoof' and model_ids is not None:
            objects = self._filter_by_model_ids(objects, model_ids)

        # make sure to return BioFile representation of a file, not the database one
        return [HighPadFile(client_id=f.client_id, path=f.path, file_id=f.path, attack_type=f.attack_type)
                for f in objects]

    def annotations(self, file):
        pass
