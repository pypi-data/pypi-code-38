import os
from pathlib import Path

HOME = str(Path.home())
DEFAULT_LOCATION = os.path.join(HOME,'.metadrive')

DATA_DIR = os.path.join(DEFAULT_LOCATION, 'data')
FILENAME_LENGTH_LIMIT = 143 # Cause ecryptfs supports max 143 chars.
