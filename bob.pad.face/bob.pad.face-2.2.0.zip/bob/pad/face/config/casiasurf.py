#!/usr/bin/env python
# encoding: utf-8

from bob.pad.face.database import CasiaSurfPadDatabase
from bob.extension import rc

database = CasiaSurfPadDatabase(
    protocol='all',
    original_directory=rc['bob.db.casiasurf.directory'],
    original_extension=".jpg",
)
