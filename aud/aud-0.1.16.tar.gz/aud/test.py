from aud import *

#logger = setupLogger()


#dirpath = AudDir("test")

#dirpath.pad(2.0,2.0)
#dirpath.renameReplaceSpaces()
#dirpath.convertTo(".wav", _target_samplerate=44100)

dir = "test"
dirpath = aud.AudDir(dir)
logger = aud.setupLogger()
logger.debug("Performing a TEST on: {0}".format(dir))
