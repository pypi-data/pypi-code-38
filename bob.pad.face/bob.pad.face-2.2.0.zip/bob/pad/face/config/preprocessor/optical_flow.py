from bob.bio.base.preprocessor import CallablePreprocessor
from bob.pad.face.extractor import OpticalFlow


def _read_original_data(biofile, directory, extension):
    return biofile.frames


preprocessor = CallablePreprocessor(OpticalFlow(), accepts_annotations=False)
preprocessor.read_original_data = _read_original_data
