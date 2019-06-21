#!/usr/bin/env python

from bob.bio.video.database import YoutubeBioDatabase

youtube_directory = "[YOUR_YOUTUBE_DIRECTORY]"

database = YoutubeBioDatabase(
    original_directory=youtube_directory,
    protocol='fold1',
    models_depend_on_protocol=True,
    training_depends_on_protocol=True,

    all_files_options={'subworld': 'fivefolds'},
    extractor_training_options={'subworld': 'fivefolds'},
    projector_training_options={'subworld': 'fivefolds'},
    enroller_training_options={'subworld': 'fivefolds'},
)
