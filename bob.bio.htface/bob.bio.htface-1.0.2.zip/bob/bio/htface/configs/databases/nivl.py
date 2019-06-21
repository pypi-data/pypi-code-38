#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import NIVLBioDatabase
from bob.extension import rc

database = NIVLBioDatabase(original_directory=rc["bob.bio.htface.nivl_path"],
                                original_extension=rc["bob.bio.htface.nivl_extension"],
                                protocol='idiap-search_VIS-NIR_split1',
                                models_depend_on_protocol = True)

# Estimated training size
samples_per_epoch = 1387 * 5
