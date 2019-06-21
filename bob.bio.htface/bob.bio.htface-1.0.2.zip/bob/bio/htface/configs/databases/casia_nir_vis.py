#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import CBSR_NIR_VIS_2BioDatabase
from bob.extension import rc

database = CBSR_NIR_VIS_2BioDatabase(original_directory=rc["bob.bio.htface.casia_nir_vis_path"],
                                original_extension=rc["bob.bio.htface.casia_nir_vis_extension"],
                                protocol='view2_1',
                                models_depend_on_protocol = True)

# Estimated training size
samples_per_epoch = 2480 * 5
