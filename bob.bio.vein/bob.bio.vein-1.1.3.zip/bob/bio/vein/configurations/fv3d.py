#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""`3D Fingervein`_ is a database for biometric fingervein recognition

The `3D Fingervein`_ Database for finger vein recognition consists of 13614
images from 141 subjects collected in various acquisition campaigns.

You can download the raw data of the `3D Fingervein`_ database by following
the link.
"""


from ..database.fv3d import Database

_fv3d_directory = "[YOUR_FV3D_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

database = Database(
    original_directory = _fv3d_directory,
    original_extension = '.png',
    )
"""The :py:class:`bob.bio.base.database.BioDatabase` derivative with fv3d
database settings

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   datafiles. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_FV3D_DIRECTORY]``. You
must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this value
to the place where you actually installed the `3D Fingervein`_ Database, as
explained in the section :ref:`bob.bio.vein.baselines`.
"""

protocol = 'central'
"""The default protocol to use for tests

You may modify this at runtime by specifying the option ``--protocol`` on the
command-line of ``verify.py`` or using the keyword ``protocol`` on a
configuration file that is loaded **after** this configuration resource.
"""
