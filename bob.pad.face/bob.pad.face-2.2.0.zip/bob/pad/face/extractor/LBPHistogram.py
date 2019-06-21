from __future__ import division
from bob.bio.base.extractor import Extractor
import bob.bio.video
import bob.ip.base
import numpy as np


class LBPHistogram(Extractor):
    """Calculates a normalized LBP histogram over an image.
    These features are implemented based on [CAM12]_.

    Parameters
    ----------
    lbptype : str
        The type of the LBP operator (regular, uniform or riu2)
    elbptype : str
        The type of extended version of LBP (regular if not extended version
        is used, otherwise transitional, direction_coded or modified)
    rad : float
        The radius of the circle on which the points are taken (for circular
        LBP)
    neighbors : int
        The number of points around the central point on which LBP is
        computed (4, 8, 16)
    circ : bool
        True if circular LBP is needed, False otherwise
    n_hor : int
        Number of blocks horizontally for spatially-enhanced LBP/MCT
        histograms. Default: 1
    n_vert
        Number of blocks vertically for spatially-enhanced LBP/MCT
        histograms. Default: 1

    Attributes
    ----------
    dtype : numpy.dtype
        If a ``dtype`` is specified in the contructor, it is assured that the
        resulting features have that dtype.
    lbp : bob.ip.base.LBP
        The LPB extractor object.
    """

    def __init__(self,
                 lbptype='uniform',
                 elbptype='regular',
                 rad=1,
                 neighbors=8,
                 circ=False,
                 dtype=None,
                 n_hor=1,
                 n_vert=1):

        super(LBPHistogram, self).__init__(
            lbptype=lbptype,
            elbptype=elbptype,
            rad=rad,
            neighbors=neighbors,
            circ=circ,
            dtype=dtype,
            n_hor=n_hor,
            n_vert=n_vert)

        elbps = {
            'regular': 'regular',
            'transitional': 'trainsitional',
            'direction_coded': 'direction-coded',
            'modified': 'regular'
        }

        if elbptype == 'modified':
            mct = True
        else:
            mct = False

        if lbptype == 'uniform':
            if neighbors == 16:
                lbp = bob.ip.base.LBP(
                    neighbors=16,
                    uniform=True,
                    circular=circ,
                    radius=rad,
                    to_average=mct,
                    elbp_type=elbps[elbptype])
            else:  # we assume neighbors==8 in this case
                lbp = bob.ip.base.LBP(
                    neighbors=8,
                    uniform=True,
                    circular=circ,
                    radius=rad,
                    to_average=mct,
                    elbp_type=elbps[elbptype])
        elif lbptype == 'riu2':
            if neighbors == 16:
                lbp = bob.ip.base.LBP(
                    neighbors=16,
                    uniform=True,
                    rotation_invariant=True,
                    radius=rad,
                    circular=circ,
                    to_average=mct,
                    elbp_type=elbps[elbptype])
            else:  # we assume neighbors==8 in this case
                lbp = bob.ip.base.LBP(
                    neighbors=8,
                    uniform=True,
                    rotation_invariant=True,
                    radius=rad,
                    circular=circ,
                    to_average=mct,
                    elbp_type=elbps[elbptype])
        else:  # regular LBP
            if neighbors == 16:
                lbp = bob.ip.base.LBP(
                    neighbors=16,
                    circular=circ,
                    radius=rad,
                    to_average=mct,
                    elbp_type=elbps[elbptype])
            else:  # we assume neighbors==8 in this case
                lbp = bob.ip.base.LBP(
                    neighbors=8,
                    circular=circ,
                    radius=rad,
                    to_average=mct,
                    elbp_type=elbps[elbptype])

        self.dtype = dtype
        self.lbp = lbp
        self.n_hor = n_hor
        self.n_vert = n_vert

    def comp_block_histogram(self, data):
        """
        Extracts LBP/MCT histograms from a gray-scale image/block.

        Takes data of arbitrary dimensions and linearizes it into a 1D vector;
        Then, calculates the histogram.
        enforcing the data type, if desired.

        Parameters
        ----------
        data : numpy.ndarray
            The preprocessed data to be transformed into one vector.

        Returns
        -------
        1D :py:class:`numpy.ndarray`
            The extracted feature vector, of the desired ``dtype`` (if
            specified)
        """
        assert isinstance(data, np.ndarray)

        # allocating the image with lbp codes
        lbpimage = np.ndarray(self.lbp.lbp_shape(data), 'uint16')
        self.lbp(data, lbpimage)  # calculating the lbp image
        hist = bob.ip.base.histogram(lbpimage, (0, self.lbp.max_label - 1),
                                     self.lbp.max_label)
        hist = hist / sum(hist)  # histogram normalization
        if self.dtype is not None:
            hist = hist.astype(self.dtype)
        return hist

    def __call__(self, data):
        """
        Extracts spatially-enhanced LBP/MCT histograms from a gray-scale image.

        Parameters
        ----------
        data : numpy.ndarray
            The preprocessed data to be transformed into one vector.

        Returns
        -------
        1D :py:class:`numpy.ndarray`
            The extracted feature vector, of the desired ``dtype`` (if
            specified)

        """

        # Make sure the data can be split into equal blocks:
        row_max = int(data.shape[0] / self.n_vert) * self.n_vert
        col_max = int(data.shape[1] / self.n_hor) * self.n_hor
        data = data[:row_max, :col_max]

        blocks = [sub_block for block in np.hsplit(data, self.n_hor) for sub_block in np.vsplit(block, self.n_vert)]

        hists = [self.comp_block_histogram(block) for block in blocks]

        hist = np.hstack(hists)

        hist = hist / len(blocks)  # histogram normalization

        return hist
