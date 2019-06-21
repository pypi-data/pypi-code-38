#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
This module provides the Dataset interface allowing the user to query the
PUT Vein database in the most obvious ways.
"""

import os
import six
from .models import File


class Database(object):

    def __init__(self):
        self.protocols = ('L_4', 'R_4', 'LR_4', 'RL_4', "R_BEAT_4",
                          'L_1', 'R_1', 'LR_1', 'RL_1', "R_BEAT_1")
        self.purposes = ('enroll', 'probe')
        self.kinds = ('palm', 'wrist')
        self.groups = ('train', 'dev', 'eval')


    def check_validity(self, l, obj, valid, default):
        """Checks validity of user input data against a set of valid values"""
        if not l:
            return default
        elif isinstance(l, six.string_types) or isinstance(l, six.integer_types):
            return self.check_validity((l,), obj, valid, default)

        for k in l:
            if k not in valid:
                raise RuntimeError('Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid))

        return l


    def client_id_from_model_id(self, model_id):
        return int(model_id.split("_")[0])


    def model_ids(self, protocol=None, groups=None, kinds=None):
        """Returns a list of model ids for the specific query by the user."""

        if protocol not in self.protocols:
            raise RuntimeError('Invalid protocol "%s". Valid values are %s' % (protocol, self.protocols))

        files = self.objects(protocol=protocol, groups=groups, kinds=kinds)

        ids = []
        splitted_protocol = protocol.split("_")

        if splitted_protocol[-1] == "4":
            for f in files:
                ids.append(str(f.client_id))
        else:  # because we test protocol name before, we now that only
            # possibility is slitted_protocol[-1] == "1"
            for f in files:
                ids.append("{}_{}".format(f.client_id, f.nr))

        ids = list(set(ids))
        return ids


    def check_ids_validity(self, ids, max_value):
        """Checks validity of client ids"""
        if not ids:
            return range(1, max_value + 1)

        invalid_ids = [x for x in ids if (x > max_value) or (x < 1)]
        if invalid_ids:
            raise RuntimeError('Invalid ids "%s". "\
            "Valid values are between 1 and %d' % (invalid_ids, max_value))

        return ids


    def objects(self, protocol=None, purposes=None, model_ids=None, groups=None, kinds=None):
        """
Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        protocol
          One of the PUT protocols. As on 08.02.2017 protocols are:

              - ``L_4``,
              - ``R_4``,
              - ``LR_4``,
              - ``RL_4``,
              - ``R_BEAT_4``,
              - ``L_1``,
              - ``R_1``,
              - ``LR_1``
              - ``RL_1``,
              - ``R_BEAT_1``.

          Protocols still contains the original protocol ('L', 'R', 'LR', 'RL')
          data, the difference is, whether each enroll model is constructed
          using all hand's images (4), or each enroll image is used as a model.
          E.g.:

          The ``R_1`` protocol, if one kind (palm / wrist) is used, each group
          (dev / eval) consists of 25*4 enroll images (each image treated as a
          separate model) and 25*8 probe images, resulting in:

              - 25*4*8 = 800 genuine comparisons,
              - (25*4)*(24*8) = 19200 zero-effort impostor comparisons,
              - 25*4*25*8 = 20'000 total comparisons.

          The ``R_4`` protocol consists of the same data as ``R_1`` but now 4
          images makes enroll model resulting in 25 enroll models per dev /
          eval group. Meaning there are:

              - 25*8 = 200 genuine SCORES;
              - 25*(24*8) = 4800 zero-effort impostor SCORES;
              - 25*25*8 = 5'000 total SCORES.

          Protocols ``R_BEAT_1`` and ``R_BEAT_4`` are new **quick test**
          protocols for BOB and BEAT platforms.

          The ``R_BEAT_1`` protocol consists only of 2 persons in dev / eval
          datasets so that databse could be effectively use for algorithm
          testing. If we use only one kind of data (palm / wrist), than for
          each group (dev / eval) we have 4*2 enroll images (each image makes
          a separate model) and 2*8 probe images resulting in:

              - 2*4*8 = 64 genuine compressions;
              - 2*4*8 = 64 zero-effort impostor compressions;
              - 4*2*2*8 = 128 total comparisons.

          The ``R_BEAT_4`` consists of the same data as ``R_BEAT_1`` but now 4
          images makes enroll model resulting in 2 enroll models per dev / eval
          group. Meaning there are:

              - 2*8 = 16 genuine SCORES;
              - 2*8 = 16 zero-effort impostor SCORES;
              - 2*2*8 = 32 total SCORES.

          **You can find more information in packages documentation.**

        purposes
          The purposes required to be retrieved ('enroll', 'probe') or a tuple
          with several of them. If 'None' is given (this is the default), it is
          considered the same as a tuple with all possible values. This field
          is ignored for the data from the "train" group.

        model_ids
          Only retrieves the files for provided of model ids.
          To enable database compatibility with ``bob.bio.vein``, ``model_ids``
          can be ``None`` or list with length ``1`` (user can't pass multiple
          ``model_ids``)
          The ``model_ids`` is a string.  If 'None' is given (this is the
          default), no filter over the ``model_ids`` is performed.
          Be careful - model ID correspond to the ENROLL data set objects
          (files), don't try to make a specific 'probe' data set query using
          the ``model_ids`` -- in any way entire probe data set will be
          returned.

        groups
          One of the groups ('train', 'dev', 'eval') or a tuple with several
          of them. If 'None' is given (this is the default), it is considered
          the same as a tuple with all possible values.

        kinds
          One of the kinds of data ('palm', 'wrist'), or a tuple with several of
          them.  If 'None' is given (this is the default), it is considered the
          same as a tuple with all possible values.

        Returns: A list of ``File`` objects.
        """
# ################## WORKAROUNDS TO CONSTRUCT MODELS FROM 1 OR 4 IMAGES########
        # this part of the code is a workaround to make the ``putvein``
        # database work with the ``bob.bio.vein``.
        # The ``new`` implementation allows protocols ending with ``4`` and
        # ``1`` for different model creation. Also it allows corresponding
        # ``model_ids`` to make the ``bob.bio.vein`` model concept work.

        # if only asking for 'probes', then ignore model_ids as all of our
        # protocols do a full probe-model scan
        if (purposes and len(purposes) == 1 and 'probe' in purposes) or \
        (purposes and len(purposes) == 1 and 'train' in purposes) or \
        (purposes and purposes == 'probe') or \
        (purposes and purposes == 'train'):
            model_ids = None

        # Check the protocol:
        if protocol not in self.protocols:
            raise RuntimeError('Invalid protocol "%s". Valid values are %s' % (protocol, self.protocols))

        # overrides ``new type`` PROTOCOL name to old type implementation,
        # where allowed PROTOCOL NAMES were 'R', 'L', 'LR', 'RL'.
        splitted_protocol = protocol.split("_")
        protocol = splitted_protocol[0]


        # deals with MODEL_IDS and converts them to old type IDS (client
        # number, an integer between 1 and 100)
        if model_ids == None:
            ids = None
            # we don't perform search by the model, so we return all files:
            nrs = range(1, 4+1)
        elif splitted_protocol[-1] == "1":
            if len(model_ids) == 1:
                ids = [int(model_ids[0].split("_")[0])]
                nrs = [int(model_ids[0].split("_")[1])]
            else:
                raise IOError("Unfortunately if ``model_ids`` are used, you can"
                              " pass just one ID")
        else: # only possibility is that splitted_protocol[-1] == "4":
            nrs = range(1, 4+1)
            ids = []
            for id in model_ids:
                ids.append(int(id.split("_")[0]))

        # extra logic for the ``BEAT`` test protocols:
        if "BEAT" in splitted_protocol:
            if ids == None:
                ids = [1,2,26,27]
            else:
                ids = self.check_ids_validity(ids, 50)
        elif protocol in ('L', 'R'):
            ids = self.check_ids_validity(ids, 50)
        else:
            ids = self.check_ids_validity(ids, 100)
# END OF THE CUSTOM LOGIC.
###############################################################################

        purposes = self.check_validity(purposes, "purposes", self.purposes, self.purposes)
        groups = self.check_validity(groups, "groups", self.groups, self.groups)
        kinds = self.check_validity(kinds, "kinds", self.kinds, self.kinds)

        # Create the result list of files
        result = []

        if protocol in ('L', 'R'):
            filtered_ids = [ (x, x) for x in ids ]
            result.extend(self._get_protocol(protocol, purposes, groups, filtered_ids, kinds, False, True, nrs))
        elif protocol == 'LR':
            if ('train' in groups) or ('dev' in groups):
                filtered_ids = [ (x, x) for x in ids if x <= 50 ]
                result.extend(self._get_protocol('L', purposes, groups, filtered_ids, kinds, False, False, nrs))
            if 'eval' in groups:
                filtered_ids = [ (x, x - 50) for x in ids if x > 50 ]
                result.extend(self._get_protocol('R', purposes, groups, filtered_ids, kinds, True, False, nrs))
        elif protocol == 'RL':
            if ('train' in groups) or ('dev' in groups):
                filtered_ids = [ (x, x) for x in ids if x <= 50 ]
                result.extend(self._get_protocol('R', purposes, groups, filtered_ids, kinds, False, False, nrs))
            if 'eval' in groups:
                filtered_ids = [ (x, x - 50) for x in ids if x > 50 ]
                result.extend(self._get_protocol('L', purposes, groups, filtered_ids, kinds, True, False, nrs))

        return result


    def _get_protocol(self, protocol, purposes, groups, ids, kinds, mirrored, split, nrs):
        result = []

        if protocol == 'L':
            side = 'Left'
        else:
            side = 'Right'

        train_processed = False

        for group in groups:

            for purpose in purposes:
                if group == 'train':
                    if train_processed:
                        continue
                    series = [1, 2, 3]
                    train_processed = True
                elif purpose == 'enroll':
                    series = [1]
                else:
                    series = [2, 3]

                if split:
                    if group == 'eval':
                        filtered_ids = [ x for x in ids if x[1] >= 26 ]
                    else:
                        filtered_ids = [ x for x in ids if x[1] <= 25 ]
                else:
                    filtered_ids = ids

                for kind in kinds:
                    kind = kind[0].upper() + kind[1:]
                    result.extend(self._get_files(kind, side, filtered_ids, series, mirrored, nrs))

        return result


    def _get_files(self, kind, side, filtered_ids, series, mirrored, nrs):
        result = []

        for id in filtered_ids:
            for serie in series:
                #for n in range(1, 5):
                for n in nrs:
                    result.append(
                        File(
                            os.path.join(
                                kind,
                                'o_%03d' % id[1],
                                side,
                                'Series_%d' % serie,
                                '%s_o%03d_%s_S%d_Nr%d.bmp' % (kind[0], id[1], side[0], serie, n)
                            ),
                            id[0],
                            mirrored
                        )
                    )

        return result

# =============================================================================
# functions for BEAT platform.
# =============================================================================
    def file_model_id(self, file, protocol):
        """
        ``file_model_id`` - is a function made for the ``BEAT`` platform.
        Function outputs the ``model_id`` according to the protocol used.

         Keyword Parameters:

        file
          The ``bob.db.putvein`` file object

        protocol
          The ``bob.db.putvein`` protocol used - one of the protocols:

              - 'L_4',
              - 'R_4',
              - 'LR_4',
              - 'RL_4',
              - 'R_BEAT_4',
              - 'L_1',
              - 'R_1',
              - 'LR_1',
              - 'RL_1',
              - 'R_BEAT_1'.

        Returns: A model_id -- a string that represents the file ``model_id``
        according to the protocol used.
        """

        # Check the protocol:
        if protocol not in self.protocols:
            raise RuntimeError('Invalid protocol "{}". Valid values are {}'.\
                               format(protocol, self.protocols))

        if protocol.endswith("4"):
            model_id = str(file.client_id)

        else:  # because we check protocol names, only option that remains is
            #    protocol.endswith("1"):
            model_id = "{}_{}".format(file.client_id, file.nr)

        return model_id
