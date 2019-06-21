#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Mon 26 Sep 2016 17:21:42 CEST

"""`PUT Vein`_ is a database for biometric palm and wrist vein recognition.

PUT Vein pattern database consists of 2400 images presenting human vein patterns.
Half of images (1200 images) contain a palm vein pattern and the remaining images contain a wrist vein pattern (another 1200 images).
Data was acquired from both hands of 50 students. Thus, it has 100 different patterns for palm and wrist region.
Pictures ware taken in 3 series, 4 pictures each, with at least one week interval between each series.
Images in database have 1280x960 resolution and are stored as 24-bit bitmap. Database consist of 2 main splits:
hand and wrist, allowing to investigate both modalities.
The reference citation is [KK10]_.

You can download the raw data of the `PUT Vein`_ database by following
the link.
"""

from ..database.putvein import PutveinBioDatabase

_putvein_directory = "[YOUR_PUTVEIN_IMAGE_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

database = PutveinBioDatabase(
    original_directory = _putvein_directory,
    original_extension = '.bmp',
    )
"""The :py:class:`bob.bio.base.database.BioDatabase` derivative with PUT Vein
database settings

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   datafiles. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_PUTVEIN_IMAGE_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this
value to the place where you actually installed the PUT Vein Database, as
explained in the section :ref:`bob.bio.vein.baselines`.
"""

protocol = 'wrist-LR_1'
"""The default protocol to use for tests

You may modify this at runtime by specifying the option ``--protocol`` on the
command-line of ``verify.py`` or using the keyword ``protocol`` on a
configuration file that is loaded **after** this configuration resource.
"""







