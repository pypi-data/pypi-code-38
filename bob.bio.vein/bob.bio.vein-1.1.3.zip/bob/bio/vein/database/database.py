#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Thu 03 Nov 2016 12:23:52 CET

"""Single sample API"""


from bob.bio.base.database.file import BioFile


class VeinBioFile(BioFile):
    """A "sample" object that is specific to vein recognition experiments


    Parameters:

      f (object): Low-level file (or sample) object that is kept inside

    """

    def __init__(self, f):
        super(VeinBioFile, self).__init__(
            client_id=f.model_id,
            path=f.path,
            file_id=f.id,
            )

        # keep copy of original low-level database file object
        self.f = f
