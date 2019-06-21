#!/usr/bin/env python
"""Aggregated Db is a database for face PAD experiments.
This database aggregates the data from 3 publicly available data-sets:
`REPLAYATTACK`_, `REPLAY-MOBILE`_ and `MSU MFSD`_.
You can download the data for the above databases by following the corresponding
links.

The reference citation for the `REPLAYATTACK`_ is [CAM12]_.
The reference citation for the `REPLAY-MOBILE`_ is [CBVM16]_.
The reference citation for the `MSU MFSD`_ is [WHJ15]_.

.. include:: links.rst
"""

from bob.pad.face.database import AggregatedDbPadDatabase

# Directory where the data files are stored.
# This directory is given in the .bob_bio_databases.txt file located in your home directory
ORIGINAL_DIRECTORY = "[YOUR_AGGREGATED_DB_DIRECTORIES]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

ORIGINAL_EXTENSION = ".mov"  # extension of the data files

database = AggregatedDbPadDatabase(
    protocol='grandtest',
    original_directory=ORIGINAL_DIRECTORY,
    original_extension=ORIGINAL_EXTENSION,
    training_depends_on_protocol=True,
)
"""The :py:class:`bob.pad.base.database.PadDatabase` derivative with Aggregated Db
database settings.

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   data files. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_AGGREGATED_DB_DIRECTORIES]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` file setting this
value to the places where you actually installed the Replay-Attack, Replay-Mobile
and MSU MFSD Databases. In particular, the paths pointing to these 3 databases
must be separated with a space. See the following note with an example of
``[YOUR_AGGREGATED_DB_DIRECTORIES]`` entry in the ``${HOME}/.bob_bio_databases.txt`` file.

.. note::

    [YOUR_AGGREGATED_DB_DIRECTORIES] = <PATH_TO_REPLAY_ATTACK> <PATH_TO_REPLAY_MOBILE> <PATH_TO_MSU_MFSD>
"""

protocol = 'grandtest'
"""The default protocol to use for reproducing the baselines.

You may modify this at runtime by specifying the option ``--protocol`` on the
command-line of ``spoof.py`` or using the keyword ``protocol`` on a
configuration file that is loaded **after** this configuration resource.
"""

groups = ["train", "dev", "eval"]
"""The default groups to use for reproducing the baselines.

You may modify this at runtime by specifying the option ``--groups`` on the
command-line of ``spoof.py`` or using the keyword ``groups`` on a
configuration file that is loaded **after** this configuration resource.
"""
