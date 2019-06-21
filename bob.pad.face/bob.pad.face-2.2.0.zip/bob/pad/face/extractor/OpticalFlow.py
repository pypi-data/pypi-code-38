from bob.bio.base import vstack_features
from bob.bio.video import FrameContainer
from bob.io.base import HDF5File
from bob.ip.optflow.liu.cg import flow
from collections import Iterator
from functools import partial
import logging

logger = logging.getLogger(__name__)


def _check_frame(frame):
    if frame.dtype == "uint8":
        return frame.astype("float64") / 255.0
    return frame.astype("float64")


class _Reader:
    def __init__(self, i1, flow_method):
        self.i1 = _check_frame(i1)
        self.flow_method = flow_method

    def __call__(self, i2):
        i2 = _check_frame(i2)
        flows = self.flow_method(self.i1, i2)[:2]
        self.i1 = i2
        return flows


class OpticalFlow(object):
    """An optical flow extractor
    For more information see :any:`bob.ip.optflow.liu.cg.flow`.

    Attributes
    ----------
    alpha : float
        Regularization weight
    inner : int
        The number of inner fixed point iterations
    iterations : int
        The number of conjugate-gradient (CG) iterations
    min_width : int
        Width of the coarsest level
    outer : int
        The number of outer fixed point iterations
    ratio : float
        Downsample ratio
    """

    def __init__(
        self,
        alpha=0.02,
        ratio=0.75,
        min_width=30,
        outer=20,
        inner=1,
        iterations=50,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.ratio = ratio
        self.min_width = min_width
        self.outer = outer
        self.inner = inner
        self.iterations = iterations

    def __call__(self, video):
        """Computes optical flows on a video
        Please note that the video should either be uint8 or float64 with values from 0
        to 1.

        Parameters
        ----------
        video : numpy.ndarray
            The video. Can be a FrameContainer, generator, bob.io.video.reader, or a
            numpy array.

        Returns
        -------
        numpy.ndarray
            The flows calculated for each pixel. The output shape will be
            [number_of_frames - 1, 2, height, width].
        """
        if isinstance(video, FrameContainer):
            video = video.as_array()
        if not isinstance(video, Iterator):
            video = iter(video)

        i1 = next(video)
        reader = _Reader(
            i1,
            partial(
                flow,
                alpha=self.alpha,
                ratio=self.ratio,
                min_width=self.min_width,
                n_outer_fp_iterations=self.outer,
                n_inner_fp_iterations=self.inner,
                n_cg_iterations=self.iterations,
            ),
        )
        flows = vstack_features(reader, video)
        shape = list(flows.shape)
        shape[0] = 2
        shape.insert(0, -1)
        return flows.reshape(shape)

    def write_feature(self, feature, feature_file):
        if not isinstance(feature_file, HDF5File):
            feature_file = HDF5File(feature_file, "w")

        feature_file.set("uv", feature)
        feature_file.set_attribute("method", "liu.cg", "uv")
        feature_file.set_attribute("alpha", self.alpha, "uv")
        feature_file.set_attribute("ratio", self.ratio, "uv")
        feature_file.set_attribute("min_width", self.min_width, "uv")
        feature_file.set_attribute("n_outer_fp_iterations", self.outer, "uv")
        feature_file.set_attribute("n_inner_fp_iterations", self.inner, "uv")
        feature_file.set_attribute("n_iterations", self.iterations, "uv")

    def read_feature(self, feature_file):
        if not isinstance(feature_file, HDF5File):
            feature_file = HDF5File(feature_file, "r")

        return feature_file["uv"]
