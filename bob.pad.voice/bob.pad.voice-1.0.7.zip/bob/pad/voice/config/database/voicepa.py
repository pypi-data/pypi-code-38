#!/usr/bin/env python

import bob.pad.voice.database


# directory where the wave files are stored
voicepa_input_dir = "[YOUR_VOICEPA_WAV_DIRECTORY]"
voicepa_input_ext = ".wav"


database = bob.pad.voice.database.VoicePAPadDatabase(
    protocol='grandtest',
    original_directory=voicepa_input_dir,
    original_extension=voicepa_input_ext,
    training_depends_on_protocol=True,
)
