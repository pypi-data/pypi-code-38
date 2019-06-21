#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import Pola_ThermalBioDatabase
from bob.extension import rc

database = Pola_ThermalBioDatabase(original_directory=rc["bob.bio.htface.polathermal_path"],
                                original_extension=rc["bob.bio.htface.polathermal_extension"],
                                protocol='VIS-thermal-overall-split1',
                                models_depend_on_protocol = True)



# Estimated training size
samples_per_epoch = 400 * 5
