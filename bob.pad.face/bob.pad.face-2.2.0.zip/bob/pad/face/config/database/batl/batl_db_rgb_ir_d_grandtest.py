#!/usr/bin/env python
"""
Idiap BATL DB is a database for face PAD experiments.
"""

from bob.pad.face.database import BatlPadDatabase

# Directory where the data files are stored.
# This directory is given in the .bob_bio_databases.txt file located in your home directory
ORIGINAL_DIRECTORY = "[YOUR_BATL_DB_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

ORIGINAL_EXTENSION = ".h5"  # extension of the data files

ANNOTATIONS_TEMP_DIR = ""  # NOTE: this variable is NOT assigned in the instance of the BatlPadDatabase, thus "rc" functionality defined in bob.extension will be involved

PROTOCOL = 'grandtest-color*infrared*depth-10'  # use 10 frames for PAD experiments

database = BatlPadDatabase(
    protocol=PROTOCOL,
    original_directory=ORIGINAL_DIRECTORY,
    original_extension=ORIGINAL_EXTENSION,
    landmark_detect_method="mtcnn",  # detect annotations using mtcnn
    exclude_attacks_list=['makeup'],
    exclude_pai_all_sets=True,  # exclude makeup from all the sets, which is the default behavior for grandtest protocol
    append_color_face_roi_annot=False)  # do not append annotations, defining ROI in the cropped face image, to the dictionary of annotations

"""The :py:class:`bob.pad.base.database.BatlPadDatabase` derivative with BATL Db
database settings.

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   data files. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_BATL_DB_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` file setting this
value to the places where you actually installed the BATL Govt database.
"""

protocol = PROTOCOL
"""
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
