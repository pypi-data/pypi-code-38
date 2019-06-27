from datasets.nlp import XYZSameFileDataset, XYZSeparateFileDataset


class MatchPyramidSameFileDataset(XYZSameFileDataset):
    """Query and doc are in the same file, each line contains two of them, with a delimiter."""
    pass


class MatchPyramidSeparateFilesDataset(XYZSeparateFileDataset):
    """Query and doc are in separate files."""
    pass
