#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import FargoDepthBioDatabase
from bob.extension import rc

database = FargoDepthBioDatabase(original_directory=rc["bob.bio.htface.fargo_path"],
                            annotation_directory=rc["bob.bio.htface.fargo_annotations"],
                            original_extension=".png",
                            protocol='view2_1',
                            models_depend_on_protocol = True)

# Estimated training size
samples_per_epoch = 2000 * 5
