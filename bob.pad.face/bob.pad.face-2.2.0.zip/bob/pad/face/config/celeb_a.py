#!/usr/bin/env python
"""`CELEBA`_ is a face makeup spoofing database adapted for face PAD experiments.


You can download the raw data of the `CELEBA`_ database by following
the link.

.. include:: links.rst

"""

from bob.pad.face.database.celeb_a import CELEBAPadDatabase

# Directory where the data files are stored.
# This directory is given in the .bob_bio_databases.txt file located in your home directory
ORIGINAL_DIRECTORY = "[YOUR_CELEB_A_DATABASE_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

ORIGINAL_EXTENSION = ""  # extension of the data files

database = CELEBAPadDatabase(
    protocol='grandtest',
    original_directory=ORIGINAL_DIRECTORY,
    original_extension=ORIGINAL_EXTENSION,
    training_depends_on_protocol=True
)
"""The :py:class:`bob.pad.base.database.PadDatabase` derivative with CELEBA
database settings.

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   data files. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_CELEBA_DATABASE_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this
value to the place where you actually installed the CELEBA Database, as
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
