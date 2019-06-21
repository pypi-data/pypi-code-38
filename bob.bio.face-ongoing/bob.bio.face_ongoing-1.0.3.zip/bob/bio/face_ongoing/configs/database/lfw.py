#!/usr/bin/env python

from bob.bio.face.database import LFWBioDatabase

lfw_directory = "[YOUR_LFW_FUNNELED_DIRECTORY]"

def create_lfw(fold_name):

    return LFWBioDatabase(original_directory=lfw_directory,
                          annotation_type='funneled',
                          protocol=fold_name,
                          training_depends_on_protocol=True,
                          models_depend_on_protocol=True,

                          all_files_options={'world_type': 'restricted'},
                          extractor_training_options={'world_type': 'restricted'},  # 'subworld' : 'twofolds'
                          projector_training_options={'world_type': 'restricted'},  # 'subworld' : 'twofolds'
                          enroller_training_options={'world_type': 'restricted'}  # 'subworld' : 'twofolds'
                          )

fold1  = create_lfw("fold1")
fold2  = create_lfw("fold2")
fold3  = create_lfw("fold3")
fold4  = create_lfw("fold4")
fold5  = create_lfw("fold5")
fold6  = create_lfw("fold6")
fold7  = create_lfw("fold7")
fold8  = create_lfw("fold8")
fold9  = create_lfw("fold9")
fold10 = create_lfw("fold10")
