#!/usr/bin/env python
"""`MSU MFSD`_ is a database for face PAD experiments.

Database created at MSU, for face-PAD experiments. The public version of the database contains
280 videos corresponding to 35 clients. The videos are grouped as 'genuine' and 'attack'.
The attack videos have been constructed from the genuine ones,
and consist of three kinds: print, iPad (video-replay), and iPhone (video-replay).
Face-locations are also provided for each frame of each video, but some (6 videos) face-locations are not reliable,
because the videos are not correctly oriented.
The reference citation is [WHJ15]_.

You can download the raw data of the `MSU MFSD`_ database by following
the link.

.. include:: links.rst
"""

from bob.pad.face.database import MsuMfsdPadDatabase

# Directory where the data files are stored.
# This directory is given in the .bob_bio_databases.txt file located in your home directory
ORIGINAL_DIRECTORY = "[YOUR_MSU_MFSD_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

ORIGINAL_EXTENSION = "none"  # extension is not used to load the data in the HLDI of this database

database = MsuMfsdPadDatabase(
    protocol='grandtest',
    original_directory=ORIGINAL_DIRECTORY,
    original_extension=ORIGINAL_EXTENSION,
    training_depends_on_protocol=True,
)
"""The :py:class:`bob.pad.base.database.PadDatabase` derivative with MSU MFSD
database settings.

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   data files. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_MSU_MFSD_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this
value to the place where you actually installed the Replay-Mobile Database, as
explained in the section :ref:`bob.pad.face.baselines`.
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
