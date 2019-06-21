from bob.bio.base.extractor import CallableExtractor
from bob.pad.face.extractor import OpticalFlow

extractor = CallableExtractor(OpticalFlow())
