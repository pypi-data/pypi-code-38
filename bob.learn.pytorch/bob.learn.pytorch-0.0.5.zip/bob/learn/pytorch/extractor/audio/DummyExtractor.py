import numpy
from bob.bio.base.extractor import Extractor

class DummyExtractor(Extractor):
  """ The Dummy class for passing the extracted embedding.

  """
  def __init__(self):
    """ Init function
    """
    super(DummyExtractor, self).__init__()
  
  def __call__(self, data):
    """__call__(data) -> feature

    This function will actually perform the feature extraction.
    It must be overwritten by derived classes.
    It takes the (preprocessed) data and returns the features extracted from the data.

    **Parameters**

    data : object (usually :py:class:`numpy.ndarray`)
      The *preprocessed* data from which features should be extracted.

    **Returns:**

    feature : object (usually :py:class:`numpy.ndarray`)
      The extracted feature.
    """
    return data