#!/usr/bin/env python

import bob.bio.face
from bob.bio.htface.database import EPRIPBioDatabase
from bob.extension import rc

database = EPRIPBioDatabase(original_directory=rc["bob.bio.htface.eprip_path"],
                                original_extension=".jpg",
                                protocol='search_split1_p2s',
                                models_depend_on_protocol = True
                                )


# Estimated training size
samples_per_epoch = 123 * 5
