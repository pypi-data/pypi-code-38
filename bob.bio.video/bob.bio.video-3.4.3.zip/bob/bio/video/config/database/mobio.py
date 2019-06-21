#!/usr/bin/env python

from bob.bio.video.database import MobioBioDatabase

mobio_video_directory = "[YOUR_MOBIO_VIDEO_DIRECTORY]"

database = MobioBioDatabase(
    original_directory=mobio_video_directory,
    original_extension=".mp4",
    protocol='male',
    models_depend_on_protocol=True,
    all_files_options={'subworld': 'twothirds-subsampled'},
    extractor_training_options={'subworld': 'twothirds-subsampled'},
    projector_training_options={'subworld': 'twothirds-subsampled'},
    enroller_training_options={'subworld': 'twothirds-subsampled'},
)


