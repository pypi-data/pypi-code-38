from bob.bio.base.preprocessor import Filename

# This preprocessor does nothing, returning just the name of the file to extract the features from:

# WARNING: if you use this, you should provide the preprocessed directory, as the database directory
# i.e. ./bin/spoof.py [config.py] --preprocessed-directory /idiap/group/biometric/databases/pad/replay/protocols/replayattack-database/
empty_preprocessor = Filename()
