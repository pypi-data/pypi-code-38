#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import CUHK_CUFSBioDatabase
from bob.extension import rc
database = CUHK_CUFSBioDatabase(cufs_database_dir=rc["bob.bio.htface.cufs_path"],
                                       arface_database_dir=rc["bob.bio.htface.arface_path"],
                                       xm2vts_database_dir=rc["bob.bio.htface.xm2vts_path"],
                                       protocol='search_split1_p2s',
                                       original_extension=rc["bob.bio.htface.cufs_extension"],
                                       models_depend_on_protocol = True)

# Estimated training size
samples_per_epoch = 404 * 5
