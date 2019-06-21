import numpy
from bob.bio.base.extractor import Extractor


class CNNFeatureBlocks(Extractor):

    """
    This is an attempt to use GMMs + CNNs
    
    Basically we take one of pooling/convolutional layers which has the format (1, w, h, #filters) and make it as features
    Per input, the feature vectors will be 

    #filters, w*h
    
    
    This link recommended L2 norm (https://www.quora.com/MLconf-2015-Seattle-When-do-I-use-zero-mean-unit-variance-normalization-vs-unit-L1-L2-normalization)
    
    """

    def __init__(
            self,
            feature_layer="pool5",
    ):
        Extractor.__init__(self, skip_extractor_training=True)

        # block parameters
        # initialize this when called for the first time
        # since caffe may not work if it is compiled to run with gpu
        self.new_feature = None
        self.feature_layer = feature_layer

    def __call__(self, image):
        """__call__(image) -> feature

        Extract features

        **Parameters:**

        image : 3D :py:class:`numpy.ndarray` (floats)
          The image to extract the features from.

        **Returns:**

        feature : 2D :py:class:`numpy.ndarray` (floats)
          The extracted features
        """

        if self.new_feature is None:
            import bob.ip.caffe_extractor
            self.new_feature = bob.ip.caffe_extractor.VGGFace(self.feature_layer)

        temp_feature = self.new_feature(image)
        feature = numpy.reshape(temp_feature, (temp_feature.shape[0], numpy.prod(temp_feature.shape[1:]))).astype("float64")
        #feature = numpy.reshape(self.new_feature(image), (512, 49)).astype("float64")
        
        # Simple normalization        
        
        #mean = numpy.mean(feature, axis=0)
        #variance = numpy.var(feature, axis=0)
        #if variance == 0.0:
        #    variance = 0.00001
        #for i in range(feature.shape[0]):
        #    feature[i] = (feature[i]-mean)/variance
        

        # L2 Normalizing 
        #norms = numpy.einsum('ij,ij->i', feature, feature)
        norms = numpy.sum(feature**2, axis=1)
        numpy.sqrt(norms, norms)

        # Handling zeros
        norms[norms == 0.0] = 1.0        
        feature /= norms[:, numpy.newaxis]

        return feature

    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass
