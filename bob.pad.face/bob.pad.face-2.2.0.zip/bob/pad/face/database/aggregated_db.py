#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# =============================================================================
from bob.pad.face.database import VideoPadFile

from bob.pad.base.database import PadDatabase

# Import HLDI for the databases to aggregate:
from bob.pad.face.database import replay as replay_hldi

from bob.pad.face.database import replay_mobile as replay_mobile_hldi

from bob.pad.face.database import msu_mfsd as msu_mfsd_hldi

from bob.bio.video.database.mobio import MobioBioFile

from bob.bio.video import FrameSelector, FrameContainer

import numpy as np

# =============================================================================
class AggregatedDbPadFile(VideoPadFile):
    """
    A high level implementation of the File class for the Aggregated Database
    uniting 4 databases: REPLAY-ATTACK, REPLAY-MOBILE, MSU MFSD and Mobio.
    """

    def __init__(self, f):
        """
        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of the File class defined in the low level db interface
            of Replay-Attack, or Replay-Mobile, or MSU MFSD, or Mobio database,
            respectively:
            in the bob.db.replay.models.py       file or
            in the bob.db.replaymobile.models.py file or
            in the bob.db.msu_mfsd_mod.models.py file or
            in the bob.db.mobio.models.py file.
        """

        self.f = f
        # this f is actually an instance of the File class that is defined in
        # bob.db.<database_name>.models and the PadFile class here needs
        # client_id, path, attack_type, file_id for initialization. We have to
        # convert information here and provide them to PadFile. attack_type is a
        # little tricky to get here. Based on the documentation of PadFile:
        # In cased of a spoofed data, this parameter should indicate what kind of spoofed attack it is.
        # The default None value is interpreted that the PadFile is a genuine or real sample.

        import bob.db.mobio

        if isinstance(f, bob.db.mobio.models.File
                      ):  # MOBIO files doen't have is_real() method

            attack_type = None

        else:

            if f.is_real():
                attack_type = None
            else:
                attack_type = 'attack'
        # attack_type is a string and I decided to make it like this for this
        # particular database. You can do whatever you want for your own database.

        file_path = self.encode_file_path(f)

        file_id = self.encode_file_id(f)

        super(AggregatedDbPadFile, self).__init__(
            client_id=f.client_id,
            path=file_path,
            attack_type=attack_type,
            file_id=file_id)

    # =========================================================================
    def encode_file_id(self, f, n=2000):
        """
        Return a modified version of the ``f.id`` ensuring uniqueness of the ids
        across all databases.

        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of the File class defined in the low level db interface
            of Replay-Attack, or Replay-Mobile, or MSU MFSD, or Mobio database,
            respectively:
            in the bob.db.replay.models.py       file or
            in the bob.db.replaymobile.models.py file or
            in the bob.db.msu_mfsd_mod.models.py file or
            in the bob.db.mobio.models.py file.

        ``n`` : :py:class:`int`
            An offset to be added to the file id for different databases is defined
            as follows: offset = k*n, where k is the database number,
            k = 0,1,2 in our case. Default: 2000.

        **Returns:**

        ``file_id`` : :py:class:`int`
            A modified version of the file id, which is now unigue accross
            all databases.
        """

        import bob.db.replay
        import bob.db.replaymobile
        import bob.db.msu_mfsd_mod
        import bob.db.mobio

        if isinstance(
                f, bob.db.replay.models.File
        ):  # check if instance of File class of LLDI of Replay-Attack

            file_id = f.id

        if isinstance(
                f, bob.db.replaymobile.models.File
        ):  # check if instance of File class of LLDI of Replay-Mobile

            file_id = np.int(f.id + n)

        if isinstance(f, bob.db.msu_mfsd_mod.models.File
                      ):  # check if instance of File class of LLDI of MSU MFSD

            file_id = np.int(f.id + 2 * n)

        if isinstance(f, bob.db.mobio.models.File
                      ):  # check if instance of File class of LLDI of Mobio

            file_id = np.int(f.id + 3 * n)

        return file_id

    # =========================================================================
    def encode_file_path(self, f):
        """
        Append the name of the database to the end of the file path separated
        with "_".

        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of the File class defined in the low level db interface
            of Replay-Attack, or Replay-Mobile, or MSU MFSD, or Mobio database,
            respectively:
            in the bob.db.replay.models.py       file or
            in the bob.db.replaymobile.models.py file or
            in the bob.db.msu_mfsd_mod.models.py file or
            in the bob.db.mobio.models.py file.

        **Returns:**

        ``file_path`` : :py:class:`str`
            Modified path to the file, with database name appended to the end
            separated with "_".
        """

        import bob.db.replay
        import bob.db.replaymobile
        import bob.db.msu_mfsd_mod
        import bob.db.mobio

        if isinstance(
                f, bob.db.replay.models.File
        ):  # check if instance of File class of LLDI of Replay-Attack

            file_path = '_'.join([f.path, 'replay'])

        if isinstance(
                f, bob.db.replaymobile.models.File
        ):  # check if instance of File class of LLDI of Replay-Mobile

            file_path = '_'.join([f.path, 'replaymobile'])

        if isinstance(f, bob.db.msu_mfsd_mod.models.File
                      ):  # check if instance of File class of LLDI of MSU MFSD

            file_path = '_'.join([f.path, 'msu_mfsd_mod'])

        if isinstance(f, bob.db.mobio.models.File
                      ):  # check if instance of File class of LLDI of Mobio

            file_path = '_'.join([f.path, 'mobio'])

        return file_path

    # =========================================================================
    def load(self, directory=None, extension='.mov',
             frame_selector=FrameSelector(selection_style='all')):
        """
        Overridden version of the load method defined in the ``VideoPadFile``.

        **Parameters:**

        ``directory`` : :py:class:`str`
            String containing the paths to all databases used in this aggregated
            database. The paths are separated with a space.

        ``extension`` : :py:class:`str`
            Extension of the video files in the REPLAY-ATTACK and REPLAY-MOBILE
            databases. The extension of files in MSU MFSD is not taken into account
            in the HighLevel DB Interface of MSU MFSD. Default: '.mov'.

        **Returns:**

        ``video_data`` : FrameContainer
            Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.
        """

        import bob.db.replay
        import bob.db.replaymobile
        import bob.db.msu_mfsd_mod
        import bob.db.mobio

        directories = directory.split(" ")

        if isinstance(
                self.f, bob.db.replay.models.File
        ):  # check if instance of File class of LLDI of Replay-Attack

            db_pad_file = replay_hldi.ReplayPadFile(
                self.f)  # replay_hldi is HLDI of Replay-Attack

            directory = directories[0]

        if isinstance(
                self.f, bob.db.replaymobile.models.File
        ):  # check if instance of File class of LLDI of Replay-Mobile

            db_pad_file = replay_mobile_hldi.ReplayMobilePadFile(
                self.f)  # replay_mobile_hldi is HLDI of Replay-Mobile

            directory = directories[1]

        if isinstance(self.f, bob.db.msu_mfsd_mod.models.File
                      ):  # check if instance of File class of LLDI of MSU MFSD

            db_pad_file = msu_mfsd_hldi.MsuMfsdPadFile(
                self.f)  # msu_mfsd_hldi is HLDI of MSU MFSD

            directory = directories[2]

        if isinstance(self.f, bob.db.mobio.models.File
                      ):  # check if instance of File class of LLDI of Mobio

            db_pad_file = MobioBioFile(
                self.f)  # msu_mfsd_hldi is HLDI of MSU MFSD

            directory = directories[3]

        if isinstance(db_pad_file, bob.bio.video.database.mobio.MobioBioFile):

            video_data = db_pad_file.load(
                directory=directory,
                extension='.mp4',
                frame_selector=frame_selector)

        else:

            video_data = db_pad_file.load(
                directory=directory, 
                extension=extension,
                frame_selector=frame_selector)

        return video_data  # video data


# =============================================================================
class AggregatedDbPadDatabase(PadDatabase):
    """
    A high level implementation of the Database class for the Aggregated Database
    uniting 3 databases: REPLAY-ATTACK, REPLAY-MOBILE and MSU MFSD. Currently this
    database supports 5 protocols, which are listed in the ``available_protocols``
    argument of this class.

    Available protocols are:

    1. "grandtest" - this protocol is using all the data available in the
       databases Replay-Attack, Replay-Mobile, MSU MFSD.

    2. "photo-photo-video" - this protocol is used to test the system on
       unseen types of attacks. In this case the attacks are splitted
       as follows:
       'train' set - only **photo** attacks are used for training,
       'dev' set   - only **photo** attacks are used for threshold tuning,
       'eval' set  - only **video** attacks are used in final evaluation.
       In this case the final performance is estimated on previously
       unseen **video** attacks.

    3. "video-video-photo" - this protocol is used to test the system on
       unseen types of attacks. In this case the attacks are splitted
       as follows:
       'train' set - only **video** attacks are used for training,
       'dev' set   - only **video** attacks are used for threshold tuning,
       'eval' set  - only **photo** attacks are used in final evaluation.
       In this case the final performance is estimated on previously
       unseen **photo** attacks.

    4. "grandtest-mobio" - this protocol is using all the data available in the
       databases Replay-Attack, Replay-Mobile, MSU MFSD plus some additional data
       from MOBIO dataset is used in the training set.

    5. "grandtest-train-eval" - this protocol is using all the data available
       in the databases Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
       'train' and 'eval' are available in this protocol. The 'dev' set is
       concatenated to the training data. When requesting 'dev' set, the
       data of the 'eval' set is returned.

    6. "grandtest-train-eval-<num_train_samples>" -
       this protocol is using all the data available in the databases
       Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
       'train' and 'eval' are available in this protocol. The 'dev' set is
       concatenated to the training data. When requesting 'dev' set, the
       data of the 'eval' set is returned.
       MOREOVER, in this protocol you can specify the number of training samples
       <num_train_samples>, which will be uniformly selected for each database
       (Replay-Attack, Replay-Mobile, MSU MFSD) used in the Aggregated DB.
       For example, in the protocol "grandtest-train-eval-5", 5 training samples
       will be selected for Replay-Attack, 5 for Replay-Mobile, and 5 for
       MSU MFSD. The total number of training samples is 15 in this case.
    """

    def __init__(
            self,
            protocol='grandtest',  # grandtest is the default protocol for this database
            original_directory=None,
            original_extension=None,
            **kwargs):
        """
        **Parameters:**

        ``protocol`` : :py:class:`str` or ``None``
            The name of the protocol that defines the default experimental setup
            for this database. Default: 'grandtest'.

        ``original_directory`` : :py:class:`str`
            String containing the paths to all databases used in this aggregated
            database. The paths are separated with a space. Default: None.

        ``original_extension`` : :py:class:`str`
            Extension of the video files in the REPLAY-ATTACK and REPLAY-MOBILE
            databases. The extension of files in MSU MFSD is not taken into account
            in the HighLevel DB Interface of MSU MFSD. Default: None.

        ``kwargs``
            The arguments of the :py:class:`bob.bio.base.database.BioDatabase`
            base class constructor.
        """

        # Import LLDI for all databases:
        import bob.db.replay
        import bob.db.replaymobile
        import bob.db.msu_mfsd_mod
        import bob.db.mobio

        self.replay_db = bob.db.replay.Database()
        self.replaymobile_db = bob.db.replaymobile.Database()
        self.msu_mfsd_db = bob.db.msu_mfsd_mod.Database()
        self.mobio = bob.db.mobio.Database()

        # Since the high level API expects different group names than what the low
        # level API offers, you need to convert them when necessary
        self.low_level_group_names = (
            'train', 'devel',
            'test')  # group names in the low-level database interface
        self.high_level_group_names = (
            'train', 'dev',
            'eval')  # names are expected to be like that in objects() function

        # A list of available protocols:
        self.available_protocols = [
            'grandtest', 'photo-photo-video', 'video-video-photo',
            'grandtest-mobio', 'grandtest-train-eval',
            'grandtest-train-eval-<num_train_samples>']

        # Always use super to call parent class methods.
        super(AggregatedDbPadDatabase, self).__init__(
            name='aggregated_db',
            protocol=protocol,
            original_directory=original_directory,
            original_extension=original_extension,
            **kwargs)

    # =========================================================================
    def get_mobio_files_given_single_group(self, groups=None, purposes=None):
        """
        Get a list of files for the MOBIO database. All files are bona-fide
        samples and used only for training. Thus, a non-empty list is returned
        only when groups='train' and purposes='real'.
        Only one file per client is selected. The files collected in Idiap are
        excluded from training set to make sure identities in 'train' set don't
        overlap with 'devel' and 'test' sets.

        **Parameters:**

        ``groups`` : :py:class:`str`
            The group of which the clients should be returned.
            One element of ('train', 'devel', 'test').

        ``purposes`` : :py:class:`str`
            OR a list of strings.
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.

        **Returns:**

        ``mobio_files`` : [File]
            A list of files, as defined in the low level interface of the MOBIO
            database.
        """

        mobio_files = []

        if (groups is not None) and ('train' in groups) and (
                purposes is not None) and ('real' in purposes):

            files_mobio = self.mobio.all_files()

            metadata = []

            for f in files_mobio:

                metadata.append((f.client_id))

            metadata_set = list(
                set(metadata))  # metadata_set is a list of unique client ids

            for f in files_mobio:

                metadata = (f.client_id)

                if metadata in metadata_set:  # only one video per client id is selected

                    metadata_set.remove(metadata)

                    if "idiap" not in f.path:
                        # videos collected at idiap are excluded to make sure identities in train set dont overlap with dev and test sets.
                        mobio_files.append(f)

        return mobio_files

    # =========================================================================
    def uniform_select_list_elements(self, data, n_samples):
        """
        Uniformly select N elements from the input data list.

        **Parameters:**

        ``data`` : []
            Input list to select elements from.

        ``n_samples`` : :py:class:`int`
            The number of samples to be selected uniformly from the input list.

        **Returns:**

        ``selected_data`` : []
            Selected subset of elements.
        """

        if len(data) <= n_samples:

            selected_data = data

        else:

            uniform_step = len(data) / np.float(n_samples + 1)

            idxs = [int(np.round(uniform_step * (x + 1)))
                    for x in range(n_samples)]

            selected_data = [data[idx] for idx in idxs]

        return selected_data

    # =========================================================================
    def get_files_given_single_group(self,
                                     groups=None,
                                     protocol=None,
                                     purposes=None,
                                     model_ids=None,
                                     **kwargs):
        """
        This function returns 4 lists of files for Raplay-Attack, Replay-Mobile,
        MSU MFSD and MOBIO databases, which fulfill the given restrictions. This
        function for the groups parameter accepts a single string ONLY, which
        determines the low level name of the group, see ``low_level_group_names``
        argument of this class for available options.

        **Parameters:**

        ``groups`` : :py:class:`str`
            The group of which the clients should be returned.
            One element of ('train', 'devel', 'test').

        ``protocol`` : :py:class:`str`
            The protocol for which the clients should be retrieved.
            Available options are defined in the ``available_protocols`` argument
            of the class. So far the following protocols are available:

            1. "grandtest" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD.

            2. "photo-photo-video" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **photo** attacks are used for training,
               'dev' set   - only **photo** attacks are used for threshold tuning,
               'eval' set  - only **video** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **video** attacks.

           3. "video-video-photo" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **video** attacks are used for training,
               'dev' set   - only **video** attacks are used for threshold tuning,
               'eval' set  - only **photo** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **photo** attacks.

            4. "grandtest-mobio" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD plus some additional data
               from MOBIO dataset is used in the training set.

            5. "grandtest-train-eval" - this protocol is using all the data available
               in the databases Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'test' are available in this protocol. The 'devel' set is
               concatenated to the training data. When requesting 'devel' set, the
               data of the 'test' set is returned.

            6. "grandtest-train-eval-<num_train_samples>" -
               this protocol is using all the data available in the databases
               Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'eval' are available in this protocol. The 'dev' set is
               concatenated to the training data. When requesting 'dev' set, the
               data of the 'eval' set is returned.
               MOREOVER, in this protocol you can specify the number of training samples
               <num_train_samples>, which will be uniformly selected for each database
               (Replay-Attack, Replay-Mobile, MSU MFSD) used in the Aggregated DB.
               For example, in the protocol "grandtest-train-eval-5", 5 training samples
               will be selected for Replay-Attack, 5 for Replay-Mobile, and 5 for
               MSU MFSD. The total number of training samples is 15 in this case.

        ``purposes`` : :py:class:`str`
            OR a list of strings.
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.

        ``model_ids``
            This parameter is not supported in PAD databases yet

        **Returns:**

        ``replay_files`` : [File]
            A list of files corresponding to Replay-Attack database.

        ``replaymobile_files`` : [File]
            A list of files corresponding to Replay-Mobile database.

        ``msu_mfsd_files`` : [File]
            A list of files corresponding to MSU MFSD database.

        ``mobio_files`` : [File]
            A list of files corresponding to MOBIO database or an empty list.
        """

        if protocol == 'grandtest' or protocol is None or groups is None:

            replay_files = self.replay_db.objects(
                protocol=protocol, groups=groups, cls=purposes, **kwargs)

            replaymobile_files = self.replaymobile_db.objects(
                protocol=protocol, groups=groups, cls=purposes, **kwargs)

            msu_mfsd_files = self.msu_mfsd_db.objects(
                group=groups, cls=purposes, **kwargs)

        if protocol == 'photo-photo-video':

            # the group names are low-level here: ('train', 'devel', 'test')
            if groups == 'train' or groups == 'devel':

                replay_files = self.replay_db.objects(
                    protocol='photo', groups=groups, cls=purposes, **kwargs)

                replaymobile_files = self.replaymobile_db.objects(
                    protocol='grandtest',
                    groups=groups,
                    cls=purposes,
                    sample_type='photo',
                    **kwargs)

                msu_mfsd_files = self.msu_mfsd_db.objects(
                    group=groups,
                    cls=purposes,
                    instrument=('print', ''),
                    **kwargs)

            if groups == 'test':

                replay_files = self.replay_db.objects(
                    protocol='video', groups=groups, cls=purposes, **kwargs)

                replaymobile_files = self.replaymobile_db.objects(
                    protocol='grandtest',
                    groups=groups,
                    cls=purposes,
                    sample_type='video',
                    **kwargs)

                msu_mfsd_files = self.msu_mfsd_db.objects(
                    group=groups,
                    cls=purposes,
                    instrument=('video_hd', 'video_mobile', ''),
                    **kwargs)

        if protocol == 'video-video-photo':

            # the group names are low-level here: ('train', 'devel', 'test')
            if groups == 'train' or groups == 'devel':

                replay_files = self.replay_db.objects(
                    protocol='video', groups=groups, cls=purposes, **kwargs)

                replaymobile_files = self.replaymobile_db.objects(
                    protocol='grandtest',
                    groups=groups,
                    cls=purposes,
                    sample_type='video',
                    **kwargs)

                msu_mfsd_files = self.msu_mfsd_db.objects(
                    group=groups,
                    cls=purposes,
                    instrument=('video_hd', 'video_mobile', ''),
                    **kwargs)

            if groups == 'test':

                replay_files = self.replay_db.objects(
                    protocol='photo', groups=groups, cls=purposes, **kwargs)

                replaymobile_files = self.replaymobile_db.objects(
                    protocol='grandtest',
                    groups=groups,
                    cls=purposes,
                    sample_type='photo',
                    **kwargs)

                msu_mfsd_files = self.msu_mfsd_db.objects(
                    group=groups,
                    cls=purposes,
                    instrument=('print', ''),
                    **kwargs)

        mobio_files = []

        if protocol == 'grandtest-mobio':

            replay_files = self.replay_db.objects(
                protocol='grandtest', groups=groups, cls=purposes, **kwargs)

            replaymobile_files = self.replaymobile_db.objects(
                protocol='grandtest', groups=groups, cls=purposes, **kwargs)

            msu_mfsd_files = self.msu_mfsd_db.objects(
                group=groups, cls=purposes, **kwargs)

            mobio_files = self.get_mobio_files_given_single_group(
                groups=groups, purposes=purposes)

        if protocol is not None:

            if 'grandtest-train-eval' in protocol:

                if groups == 'train':

                    replay_files = self.replay_db.objects(
                        protocol='grandtest',
                        groups=['train', 'devel'],
                        cls=purposes,
                        **kwargs)

                    replaymobile_files = self.replaymobile_db.objects(
                        protocol='grandtest',
                        groups=['train', 'devel'],
                        cls=purposes,
                        **kwargs)

                    msu_mfsd_files = self.msu_mfsd_db.objects(
                        group=['train', 'devel'], cls=purposes, **kwargs)

                    if len(protocol) > len('grandtest-train-eval'):

                        num_train_samples = [
                            int(s) for s in protocol.split("-") if s.isdigit()][-1]

                        replay_files = self.uniform_select_list_elements(
                            data=replay_files, n_samples=num_train_samples)
                        replaymobile_files = self.uniform_select_list_elements(
                            data=replaymobile_files, n_samples=num_train_samples)
                        msu_mfsd_files = self.uniform_select_list_elements(
                            data=msu_mfsd_files, n_samples=num_train_samples)

                if groups in ['devel', 'test']:

                    replay_files = self.replay_db.objects(
                        protocol='grandtest',
                        groups='test',
                        cls=purposes,
                        **kwargs)

                    replaymobile_files = self.replaymobile_db.objects(
                        protocol='grandtest',
                        groups='test',
                        cls=purposes,
                        **kwargs)

                    msu_mfsd_files = self.msu_mfsd_db.objects(
                        group='test', cls=purposes, **kwargs)

        return replay_files, replaymobile_files, msu_mfsd_files, mobio_files

    # =========================================================================
    def get_files_given_groups(self,
                               groups=None,
                               protocol=None,
                               purposes=None,
                               model_ids=None,
                               **kwargs):
        """
        This function returns 4 lists of files for Raplay-Attack, Replay-Mobile,
        MSU MFSD and MOBIO databases, which fulfill the given restrictions. This
        function for the groups parameter accepts a single string OR a list
        of strings with multiple groups. Group names are low level, see
        ``low_level_group_names`` argument of the class for available options.

        Keyword parameters:

        ``groups`` : :py:class:`str`
            OR a list of strings.
            The groups of which the clients should be returned.
            Usually, groups are one or more elements of ('train', 'devel', 'test').

        ``protocol`` : :py:class:`str`
            The protocol for which the clients should be retrieved.
            Available options are defined in the ``available_protocols`` argument
            of the class. So far the following protocols are available:

            1. "grandtest" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD.

            2. "photo-photo-video" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **photo** attacks are used for training,
               'dev' set   - only **photo** attacks are used for threshold tuning,
               'eval' set  - only **video** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **video** attacks.

           3. "video-video-photo" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **video** attacks are used for training,
               'dev' set   - only **video** attacks are used for threshold tuning,
               'eval' set  - only **photo** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **photo** attacks.

            4. "grandtest-mobio" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD plus some additional data
               from MOBIO dataset is used in the training set.

            5. "grandtest-train-eval" - this protocol is using all the data available
               in the databases Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'test' are available in this protocol. The 'devel' set is
               concatenated to the training data. When requesting 'devel' set, the
               data of the 'test' set is returned.

            6. "grandtest-train-eval-<num_train_samples>" -
               this protocol is using all the data available in the databases
               Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'eval' are available in this protocol. The 'dev' set is
               concatenated to the training data. When requesting 'dev' set, the
               data of the 'eval' set is returned.
               MOREOVER, in this protocol you can specify the number of training samples
               <num_train_samples>, which will be uniformly selected for each database
               (Replay-Attack, Replay-Mobile, MSU MFSD) used in the Aggregated DB.
               For example, in the protocol "grandtest-train-eval-5", 5 training samples
               will be selected for Replay-Attack, 5 for Replay-Mobile, and 5 for
               MSU MFSD. The total number of training samples is 15 in this case.

        ``purposes`` : :py:class:`str`
            OR a list of strings.
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.

        ``model_ids``
            This parameter is not supported in PAD databases yet

        **Returns:**

        ``replay_files`` : [File]
            A list of files corresponding to Replay-Attack database.

        ``replaymobile_files`` : [File]
            A list of files corresponding to Replay-Mobile database.

        ``msu_mfsd_files`` : [File]
            A list of files corresponding to MSU MFSD database.

        ``mobio_files`` : [File]
            A list of files corresponding to MOBIO database or an empty list.
        """

        if isinstance(groups,
                      str) or groups is None:  # if a single group is given

            groups = [groups]

        replay_files = []

        replaymobile_files = []

        msu_mfsd_files = []

        mobio_files = []

        for group in groups:

            files = self.get_files_given_single_group(
                groups=group,
                protocol=protocol,
                purposes=purposes,
                model_ids=model_ids,
                **kwargs)

            replay_files += files[0]

            replaymobile_files += files[1]

            msu_mfsd_files += files[2]

            mobio_files += files[3]

        return replay_files, replaymobile_files, msu_mfsd_files, mobio_files

    # =========================================================================
    def objects(self,
                groups=None,
                protocol=None,
                purposes=None,
                model_ids=None,
                **kwargs):
        """
        This function returns a list of AggregatedDbPadFile objects, which fulfill the given restrictions.

        Keyword parameters:

        ``groups`` : :py:class:`str`
            OR a list of strings.
            The groups of which the clients should be returned.
            Usually, groups are one or more elements of ('train', 'dev', 'eval')

        ``protocol`` : :py:class:`str`
            The protocol for which the clients should be retrieved.
            Available options are defined in the ``available_protocols`` argument
            of the class. So far the following protocols are available:

            1. "grandtest" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD.

            2. "photo-photo-video" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **photo** attacks are used for training,
               'dev' set   - only **photo** attacks are used for threshold tuning,
               'eval' set  - only **video** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **video** attacks.

           3. "video-video-photo" - this protocol is used to test the system on
               unseen types of attacks. In this case the attacks are splitted
               as follows:
               'train' set - only **video** attacks are used for training,
               'dev' set   - only **video** attacks are used for threshold tuning,
               'eval' set  - only **photo** attacks are used in final evaluation.
               In this case the final performance is estimated on previously
               unseen **photo** attacks.

            4. "grandtest-mobio" - this protocol is using all the data available in the
               databases Replay-Attack, Replay-Mobile, MSU MFSD plus some additional data
               from MOBIO dataset is used in the training set.

            5. "grandtest-train-eval" - this protocol is using all the data available
               in the databases Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'eval' are available in this protocol. The 'dev' set is
               concatenated to the training data. When requesting 'dev' set, the
               data of the 'eval' set is returned.

            6. "grandtest-train-eval-<num_train_samples>" -
               this protocol is using all the data available in the databases
               Replay-Attack, Replay-Mobile, MSU MFSD. Only two gropus
               'train' and 'eval' are available in this protocol. The 'dev' set is
               concatenated to the training data. When requesting 'dev' set, the
               data of the 'eval' set is returned.
               MOREOVER, in this protocol you can specify the number of training samples
               <num_train_samples>, which will be uniformly selected for each database
               (Replay-Attack, Replay-Mobile, MSU MFSD) used in the Aggregated DB.
               For example, in the protocol "grandtest-train-eval-5", 5 training samples
               will be selected for Replay-Attack, 5 for Replay-Mobile, and 5 for
               MSU MFSD. The total number of training samples is 15 in this case.

        ``purposes`` : :py:class:`str`
            OR a list of strings.
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.

        ``model_ids``
            This parameter is not supported in PAD databases yet

        **Returns:**

        ``files`` : [AggregatedDbPadFile]
            A list of AggregatedDbPadFile objects.
        """

        # Convert group names to low-level group names here.
        groups = self.convert_names_to_lowlevel(
            groups, self.low_level_group_names, self.high_level_group_names)
        # Since this database was designed for PAD experiments, nothing special
        # needs to be done here.

        replay_files, replaymobile_files, msu_mfsd_files, mobio_files = self.get_files_given_groups(
            groups=groups,
            protocol=protocol,
            purposes=purposes,
            model_ids=model_ids,
            **kwargs)

        files = replay_files + replaymobile_files + msu_mfsd_files + \
            mobio_files  # append all files to a single list

        files = [AggregatedDbPadFile(f) for f in files]

        return files

    # =========================================================================
    def annotations(self, f):
        """
        Return annotations for a given file object ``f``, which is an instance
        of ``AggregatedDbPadFile`` defined in the HLDI of the Aggregated DB.
        The ``load()`` method of ``AggregatedDbPadFile`` class (see above)
        returns a video, therefore this method returns bounding-box annotations
        for each video frame. The annotations are returned as dictionary of
        dictionaries.

        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of ``AggregatedDbPadFile`` defined above.

        **Returns:**

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.

        """

        import bob.db.replay
        import bob.db.replaymobile
        import bob.db.msu_mfsd_mod

        directories = self.original_directory.split(" ")

        if isinstance(
                f.f, bob.db.replay.models.File
        ):  # check if instance of File class of LLDI of Replay-Attack

            hldi_db = replay_hldi.ReplayPadDatabase(
                original_directory=directories[0])

        if isinstance(
                f.f, bob.db.replaymobile.models.File
        ):  # check if instance of File class of LLDI of Replay-Mobile

            hldi_db = replay_mobile_hldi.ReplayMobilePadDatabase(
                original_directory=directories[1])

        if isinstance(f.f, bob.db.msu_mfsd_mod.models.File
                      ):  # check if instance of File class of LLDI of MSU MFSD

            hldi_db = msu_mfsd_hldi.MsuMfsdPadDatabase(
                original_directory=directories[2])

        if self.protocol == "grandtest-mobio" or isinstance(
                f.f, bob.db.mobio.models.File
        ):  # annotations are not available for this protocol

            annotations = {}

        else:

            annotations = hldi_db.annotations(f)

        return annotations
