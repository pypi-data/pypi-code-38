from .mixins.reading import AnnotationsReadMixin, ImageListReadingMixin
from .mixins.parts import PartMixin, RevealedPartMixin, CroppedPartMixin
from .mixins.features import PreExtractedFeaturesMixin
from .mixins.chainer_mixins import IteratorMixin


class ImageWrapperDataset(PartMixin, PreExtractedFeaturesMixin, AnnotationsReadMixin, IteratorMixin):
	pass

class Dataset(ImageWrapperDataset):

	def get_example(self, i):
		im_obj = super(Dataset, self).get_example(i)
		return im_obj.as_tuple()
