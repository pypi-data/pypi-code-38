"""
    HAND RDF - Features

    Description:
    All the utilities to create and manage the offsets for the hand segmentation
    with the RDF are contained in this file.

    Author:
    Bernat Galmés Rubert

    Year:
    2018

    Universitat de les Illes Balears
"""
import math
import cv2
import numpy as np
import pandas as pd

from .Model.Config import config


def get_dataframe_offsets(df):
    """
    From a Dataframe with the columns:
    'ux': X values of u offsets
    'uy': y values of u offsets
    'vx': X values of v offsets
    'vy': y values of v offsets

    Get a ndarray of the offsets with the format
    used by class Features.

    Usefull function to use with: Features.set_offsets().
    To configure offsets manually.

    :param df: DataFrame with the previous described structure
    :return:
    ndarray with shape(n_offsets, 2, 2)
    """
    config.N_FEATURES = len(df)
    offsets = np.zeros((config.N_FEATURES, 2, 2), dtype=np.float64)

    offsets[:, 0, 0] = df['uy']
    offsets[:, 0, 1] = df['ux']
    offsets[:, 1, 0] = df['vy']
    offsets[:, 1, 1] = df['vx']
    return offsets


class Features:
    """
    Class to generate and manage offsets as features in the hand RDF problem.
    """

    def __init__(self, all_offsets=config.OFFSETS_USE_ALL):
        """

        :param all_offsets: bool
        True if want to generate all offsets,
        False if only want to load the offsets specified in config.FILE_OFFSETS file
        """
        np.random.seed(config.OFFSETS_SEED)

        if all_offsets:
            self._offset = self.generate_offsets(config.OFFSETS_DISTRIBUTION)

        else:
            offsets = pd.read_excel(config.FILE_OFFSETS, sheet_name='OFFSETS',
                                    convert_float=False)
            ux = offsets['ux'].as_matrix()
            uy = offsets['uy'].as_matrix()
            vx = offsets['vx'].as_matrix()
            vy = offsets['vy'].as_matrix()

            u = np.stack((uy, ux), axis=1)
            v = np.stack((vy, vx), axis=1)
            self._offset = np.stack((u, v), axis=1)

            # set configuration
            config.N_FEATURES = len(ux)

    def get_image_features(self, image, positions):
        """
        Given a depth image and a set of (x, y) positions,
        get the features of the pixels in the image specified by the positions.

        :param image: uint16 ndarray The depth image to use
        :param positions: List|ndarray of the (x, y) positions to compute the features.

        :return: Tuple list, ndarray
        A list with the positions of the features computed.
        An ndarray of shape (len(positions), len(offsets)) with the features computed in each position.

        """
        max_depth = np.max(image)
        h, w = image.shape
        depths = image[positions]

        features = np.zeros((len(positions[0]), len(self._offset)), dtype=np.float64)
        offsets = (positions + self._offset[:, :, :, np.newaxis] / depths).astype(np.uint16)

        du = np.full(len(positions[0]), max_depth, dtype=np.int16)
        dv = np.full(len(positions[0]), max_depth, dtype=np.int16)

        # compute indexs inside image
        off_in = np.logical_and(offsets[:, :, 0, :] < h, offsets[:, :, 1, :] < w)
        for i, off in enumerate(offsets):
            offsets_u, offsets_v = off
            u_off_in, v_off_in = off_in[i]

            du[:] = max_depth
            dv[:] = max_depth

            dv[v_off_in] = image[(offsets_v[0][v_off_in], offsets_v[1][v_off_in])]
            du[u_off_in] = image[(offsets_u[0][u_off_in], offsets_u[1][u_off_in])]

            features[:, i] = du - dv

        features = (np.around(features, decimals=config.ROUND_VALUES)/100).astype(np.int8)

        return positions, features

    def get_im_offset(self, n_feat):
        """
        Get a debug image of the offset specified by parameter.

        :param n_feat: string|int
        Name of the feature offset or the position of the offset in the set.

        :return:
        ndarray RGB representation of the specified offset
        """
        size_im = 500
        mid_y, mid_x = (np.array([size_im, size_im]) / 2).astype(np.uint16)

        if isinstance(n_feat, str):
            n_feat = int(n_feat.split("_")[1])

        off = self._offset[n_feat]
        (uoff_y, uoff_x), (voff_y, voff_x) = ((off / config.OFFSET_MAX) * (size_im / 3)).astype(np.int16)

        im_offset = np.full((size_im, size_im, 3), 255, dtype=np.uint8)

        cv2.line(im_offset, (mid_x - 5, mid_y), (mid_x + 5, mid_y), (0, 0, 0), 3)
        cv2.line(im_offset, (mid_x, mid_y - 5), (mid_x, mid_y + 5), (0, 0, 0), 3)

        cv2.putText(im_offset, 'u', (mid_x + uoff_x, mid_y + uoff_y + 5),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2)
        cv2.circle(im_offset, (mid_x + uoff_x, mid_y + uoff_y), 5, (0, 255, 0), -1)
        cv2.putText(im_offset, 'v', (mid_x + voff_x, mid_y + voff_y + 5),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 127, 127), 2)
        cv2.circle(im_offset, (mid_x + voff_x, mid_y + voff_y), 5, (0, 127, 127), -1)

        return im_offset

    def set_offsets(self, offsets):
        """
        Set offsets generated externally from class

        :param offsets: ndarray with the offsets build in the format used by the class
        :return: None
        """
        self._offset = offsets

    def get_metaData(self):
        """
        Get a dictionary with the basic internal info
        of the offsets configuration.
        :return:
        """
        return {
            "OFFSET_DISTRIBUTION": config.OFFSETS_DISTRIBUTION,
            "OFFSET_MAX": config.OFFSET_MAX,
            "OFFSET_SEED": config.OFFSETS_SEED,
            "OFFSET_NUM": config.N_FEATURES
        }

    def as_DataFrame(self):
        """
        Transform the offsets contained in the class in a DataFrame.
        DataFrame with columns:
        'ux': X values of u offsets
        'uy': y values of u offsets
        'vx': X values of v offsets
        'vy': y values of v offsets

        :return:
        DataFrame The builded DataFrame
        """
        res = {
            "feat": np.arange(0, len(self._offset[:, 0, 0])),
            "ux": self._offset[:, 0, 0],
            "uy": self._offset[:, 0, 1],
            "vx": self._offset[:, 1, 0],
            "vy": self._offset[:, 1, 1]
        }

        return pd.DataFrame(res)

    @staticmethod
    def generate_offsets(dist):
        """
        Generate the feature offsets following the specified distribution in the parameter

        :param dist: string Distribution that must follow the offsets
        :return: ndarray the offsets genereted
        """
        if dist == "NORMAL":
            offsets = np.random.normal(0, config.OFFSET_MAX, (config.N_OFFSETS, 2, 2)).astype(np.float64)

        elif dist == "UNIFORM":
            offsets = np.random.uniform(-config.OFFSET_MAX, config.OFFSET_MAX, (config.N_FEATURES, 2, 2)).astype(np.float64)

        elif dist == "CIRCULARUNIFORM":
            alphas = np.random.rand(2, config.N_OFFSETS) * 359
            max_r = math.sqrt(2 * config.OFFSET_MAX**2)
            rads = np.random.rand(2, config.N_OFFSETS) * max_r

            offsets = np.zeros((config.N_FEATURES, 2, 2))
            offsets[:, 0, 0] = np.sin(alphas[0]) * rads[0]
            offsets[:, 0, 1] = np.cos(alphas[0]) * rads[0]
            offsets[:, 1, 0] = np.sin(alphas[1]) * rads[1]
            offsets[:, 1, 1] = np.cos(alphas[1]) * rads[1]

        elif dist == "GENERATED":
            df = pd.read_excel(config.FOLDER_OFFSETS + "offsets_generated.xlsx", sheet_name='OFFSETS')
            offsets = get_dataframe_offsets(df)
            return offsets

        elif dist == "DEPURED":
            offsets = pd.read_excel(config.FOLDER_OFFSETS + "offsets_treeFeatures.xlsx",
                                    sheet_name='depured_offsets')
            offsets = get_dataframe_offsets(offsets)
            return offsets

        elif dist == "SELECTED":
            offsets = pd.read_excel(config.FOLDER_OFFSETS + "offsets_treeFeatures.xlsx",
                                    sheet_name='selected_offsets')
            offsets = get_dataframe_offsets(offsets)
            return offsets

        else:
            raise Exception("Incorrect offsets distribution")

        # a half of candidates either u or v putted to 0
        offsets[list(np.arange(0, len(offsets), 4)), 0] = [0., 0.]
        offsets[list(np.arange(1, len(offsets), 4)), 1] = [0., 0.]

        return offsets
