# vim: set fileencoding=utf-8 :
# Mon 26 Sep 2016 17:21:42 CEST

"""`VERA Fingervein`_ is a database for presentation attack detection

It consists of 880 images from 110 clients (half of those are presentation
attacks). It was produced at the Idiap Research Institute in Martigny and at
Haute Ecole Spécialisée de Suisse Occidentale in Sion, in Switzerland. The
reference citations are [TVM14]_ and [TREA15]_.

You can download the raw data of the `VERA Fingervein`_ database by following
the link.
"""


from ..database import VerafingerPadDatabase

_verafinger_directory = "[YOUR_VERAFINGER_DIRECTORY]"
"""Value of ``~/.bob_bio_databases.txt`` for this database"""

database = VerafingerPadDatabase(
    original_directory = _verafinger_directory,
    original_extension = '.png',
    )
"""The :py:class:`bob.pad.base.database.PadDatabase` derivative with Verafinger
database settings

.. warning::

   This class only provides a programmatic interface to load data in an orderly
   manner, respecting usage protocols. It does **not** contain the raw
   datafiles. You should procure those yourself.

Notice that ``original_directory`` is set to ``[YOUR_VERAFINGER_DIRECTORY]``.
You must make sure to create ``${HOME}/.bob_bio_databases.txt`` setting this
value to the place where you actually installed the Verafinger Database, as
explained in the section :ref:`bob.pad.vein.baselines`.
"""

protocol = 'full'
"""The default protocol to use for tests

You may modify this at runtime by specifying the option ``--protocol`` on the
command-line of ``spoof.py`` or using the keyword ``protocol`` on a
configuration file that is loaded **after** this configuration resource.

We accept any PAD protocol implemented by bob.db.verafinger.
"""

groups = ["train", "dev", "eval"]
"""The default groups to use for reproducing the baselines.

You may modify this at runtime by specifying the option ``--groups`` on the
command-line of ``spoof.py`` or using the keyword ``groups`` on a configuration
file that is loaded **after** this configuration resource.  """
