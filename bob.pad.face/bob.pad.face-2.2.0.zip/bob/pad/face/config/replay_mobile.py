#!/usr/bin/env python
"""`Replay-Mobile`_ is a database for face PAD experiments.

The Replay-Mobile Database for face spoofing consists of 1030 video clips of photo and video attack attempts to 40 clients,
under different lighting conditions.
These videos were recorded with current devices from the market -- an iPad Mini2 (running iOS) and a LG-G4 smartphone (running Android).
This Database was produced at the Idiap Research Institute (Switzerland) within the framework
of collaboration with Galician Research and Development Center in Advanced Telecommunications - Gradiant (Spain).
The reference citation is [CBVM16]_.

You can download the raw data of the `Replay-Mobile`_ database by following
the link.

.. include:: links.rst
"""

from bob.pad.face.database import ReplayMobilePadDatabase

# Directory where the data files are stored.
# This directory is given in the .bob_bio_databases.txt file located in your home directory
ORIGINAL_DIRECTORY = "[YOUR_REPLAY_MOBILE_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

ORIGINAL_EXTENSION = ".mov"  # extension of the data files

database = ReplayMobilePadDatabase(
    protocol='grandtest',
    original_directory=ORIGINAL_DIRECTORY,
    original_extension=ORIGINAL_EXTENSION,
    training_depends_on_protocol=True,
)
"""The :py:class:`bob.pad.base.database.PadDatabase` derivative with Replay-Mobile
database settings.

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   data files. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_REPLAY_MOBILE_DIRECTORY]``.
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
