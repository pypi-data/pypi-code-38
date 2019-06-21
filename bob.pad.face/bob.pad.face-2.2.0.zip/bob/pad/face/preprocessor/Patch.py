from ..utils import extract_patches
from bob.bio.base.preprocessor import Preprocessor
from bob.bio.video import FrameContainer
from bob.bio.video.preprocessor import Wrapper
from collections import OrderedDict


class ImagePatches(Preprocessor):
    """Extracts patches of images and returns it in a FrameContainer. You need
    to wrap the further blocks (extractor and algorithm) that come after this
    in bob.bio.video wrappers.
    """

    def __init__(self, block_size, block_overlap=(0, 0), n_random_patches=None,
                 **kwargs):
        super(ImagePatches, self).__init__(**kwargs)
        self.block_size = block_size
        self.block_overlap = block_overlap
        self.n_random_patches = n_random_patches

    def __call__(self, image, annotations=None):
        fc = FrameContainer()

        patches = extract_patches(image, self.block_size, self.block_overlap,
                                  self.n_random_patches)
        for i, patch in enumerate(patches):
            fc.add(i, patch)

        if not len(fc):
            return None

        return fc


class VideoPatches(Wrapper):
    """Extracts patches of images from video containers and returns it in a
    FrameContainer.
    """

    def __init__(self, block_size, block_overlap=(0, 0), n_random_patches=None,
                 normalizer=None,
                 **kwargs):
        super(VideoPatches, self).__init__(**kwargs)
        self.block_size = block_size
        self.block_overlap = block_overlap
        self.n_random_patches = n_random_patches
        self.normalizer = normalizer

    def __call__(self, frames, annotations=None):
        fc = FrameContainer()

        if self.normalizer is not None:
            annotations = OrderedDict(self.normalizer(annotations))

        for index, frame, _ in frames:

            # if annotations are given, and if particular frame annotations are
            # not missing we take them:
            annots = annotations[index] if annotations is not None and \
                index in annotations else None

            # preprocess image (by default: detect a face)
            preprocessed = self.preprocessor(frame, annots)
            if preprocessed is None:
                continue

            # extract patches
            patches = extract_patches(
                preprocessed, self.block_size, self.block_overlap,
                self.n_random_patches)
            for i, patch in enumerate(patches):
                fc.add('{}_{}'.format(index, i), patch)

        if not len(fc):
            return None

        return fc
