#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import LDHFBioDatabase
from bob.extension import rc

database = LDHFBioDatabase(original_directory=rc["bob.bio.htface.ldhf_path"],
                            original_extension=rc["bob.bio.htface.ldhf_extension"],
                            protocol='split1',
                            models_depend_on_protocol = True)

# Estimated training size
samples_per_epoch = 2000 * 5
