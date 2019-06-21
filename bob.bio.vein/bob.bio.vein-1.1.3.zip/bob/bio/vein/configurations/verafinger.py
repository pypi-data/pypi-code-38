#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Mon 26 Sep 2016 17:21:42 CEST

"""`VERA Fingervein`_ is a database for biometric fingervein recognition

It consists of 440 images from 110 clients. It was produced at the Idiap
Research Institute in Martigny and at Haute Ecole Spécialisée de Suisse
Occidentale in Sion, in Switzerland. The reference citation is [TVM14]_.

You can download the raw data of the `VERA Fingervein`_ database by following
the link.
"""


from ..database.verafinger import Database

_verafinger_directory = "[YOUR_VERAFINGER_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

database = Database(
    original_directory = _verafinger_directory,
    original_extension = '.png',
    )
"""The :py:class:`bob.bio.base.database.BioDatabase` derivative with Verafinger
database settings

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   datafiles. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_VERAFINGER_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this
value to the place where you actually installed the Verafinger Database, as
explained in the section :ref:`bob.bio.vein.baselines`.
"""

protocol = 'Nom'
"""The default protocol to use for tests

You may modify this at runtime by specifying the option ``--protocol`` on the
command-line of ``verify.py`` or using the keyword ``protocol`` on a
configuration file that is loaded **after** this configuration resource.

We accept any biometric recognition protocol implemented by bob.db.verafinger.
Variants of the biometric recognition protocol ending in ``-va`` can be used to
test for vulnerability analysis. For example, use the protocol ``Nom-va`` to
test the vulnerability of a biometric recognition pipeline using the ``Nom``
protocol for enrollment and probe samples from presentation attacks.
"""
