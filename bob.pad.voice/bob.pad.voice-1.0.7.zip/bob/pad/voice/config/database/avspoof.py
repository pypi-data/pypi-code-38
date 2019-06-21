#!/usr/bin/env python

import bob.pad.voice.database


# directory where the wave files are stored
avspoof_input_dir = "[YOUR_AVSPOOF_WAV_DIRECTORY]"
avspoof_input_ext = ".wav"


database = bob.pad.voice.database.AVspoofPadDatabase(
    protocol='grandtest',
    original_directory=avspoof_input_dir,
    original_extension=avspoof_input_ext,
    training_depends_on_protocol=True,
)
