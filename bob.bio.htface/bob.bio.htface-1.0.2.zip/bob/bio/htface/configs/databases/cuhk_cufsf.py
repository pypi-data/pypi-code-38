#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import CUHK_CUFSFBioDatabase
from bob.extension import rc

database = CUHK_CUFSFBioDatabase(original_directory=rc["bob.bio.htface.cufsf_path"],
                                original_extension=rc["bob.bio.htface.cufsf_extension"],
                                feret_directory=rc["bob.bio.htface.feret_path"],
                                protocol='search_split1_p2s',
                                models_depend_on_protocol = True
                                )


# Estimated training size
samples_per_epoch = 700 * 5
