#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 2017

@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

from bob.bio.base.preprocessor import Preprocessor

import bob.bio.video

import numpy as np

import random
random.seed(7)

from sklearn.decomposition import SparseCoder

import bob.io.base


#==============================================================================
class VideoSparseCoding(Preprocessor, object):
    """
    This class is designed to compute sparse codes for spatial frontal,
    spatio-temporal horizontal, and spatio-temporal vertical patches.
    The codes are computed for all possible stacks of facial images.
    The maximum possible number of stacks is:
    (``num_of_frames_in_video`` - ``block_length``).
    However, this number can be smaller, and is controlled by two arguments
    of this class: ``min_face_size`` and ``frame_step``.

    **Parameters:**

    ``block_size`` : :py:class:`int`
        The spatial size of facial patches. Default: 5 .

    ``block_length`` : :py:class:`int`
        The temporal length of the stack of facial images / number of frames
        per stack. Default: 10 .

    ``min_face_size`` : :py:class:`int`
        Discard frames with face of the size less than ``min_face_size``.
        Default: 50 .

    ``norm_face_size`` : :py:class:`int`
        The size of the face after normalization. Default: 64 .

    ``dictionary_file_names`` : [:py:class:`str`]
        A list of filenames containing the dictionaries. The filenames must be
        listed in the following order:
        [file_name_pointing_to_frontal_dictionary,
        file_name_pointing_to_horizontal_dictionary,
        file_name_pointing_to_vertical_dictionary]

    ``frame_step`` : :py:class:`int`
        Selected frames for processing with this step. If set to 1, all frames
        will be processes. Used to speed up the experiments.
        Default: 1.

    ``extract_histograms_flag`` : :py:class:`bool`
        If this flag is set to ``True`` the histograms of sparse codes will be
        computed for all stacks of facial images / samples. In this case an
        empty feature extractor must be used, because feature vectors (histograms)
        are already extracted in the preprocessing step.

        NOTE: set this flag to``True`` if you want to reduce the amount of
        memory required to store temporary files.
        Default: ``False``.

    ``method`` : :py:class:`str`
        A method to use in the histogram computation. Two options are available:
        "mean" and "hist". This argument is valid only if ``extract_histograms_flag``
        is set to ``True``.
        Default: "hist".

    ``comp_reconstruct_err_flag`` : :py:class:`bool`
        If this flag is set to ``True`` resulting feature vector will be a
        reconstruction error, not a histogram.
        Default: ``False``.
    """

    #==========================================================================
    def __init__(self,
                 block_size=5,
                 block_length=10,
                 min_face_size=50,
                 norm_face_size=64,
                 dictionary_file_names=[],
                 frame_step=1,
                 extract_histograms_flag=False,
                 method="hist",
                 comp_reconstruct_err_flag=False,
                 **kwargs):

        super(VideoSparseCoding, self).__init__(
            block_size=block_size,
            block_length=block_length,
            min_face_size=min_face_size,
            norm_face_size=norm_face_size,
            dictionary_file_names=dictionary_file_names,
            frame_step=frame_step,
            extract_histograms_flag=extract_histograms_flag,
            comp_reconstruct_err_flag=comp_reconstruct_err_flag,
            method=method)

        self.block_size = block_size
        self.block_length = block_length
        self.min_face_size = min_face_size
        self.norm_face_size = norm_face_size
        self.dictionary_file_names = dictionary_file_names
        self.frame_step = frame_step
        self.extract_histograms_flag = extract_histograms_flag
        self.method = method
        self.comp_reconstruct_err_flag = comp_reconstruct_err_flag

        self.video_preprocessor = bob.bio.video.preprocessor.Wrapper()

    #==========================================================================
    def crop_norm_face_grayscale(self, image, annotations, face_size):
        """
        This function crops the face in the input Gray-scale image given
        annotations defining the face bounding box. The size of the face is
        also normalized to the pre-defined dimensions.

        The algorithm is identical to the following paper:
        "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing"

        **Parameters:**

        ``image`` : 2D :py:class:`numpy.ndarray`
            Gray-scale input image.

        ``annotations`` : :py:class:`dict`
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows:
            ``{'topleft': (row, col), 'bottomright': (row, col)}``

        ``face_size`` : :py:class:`int`
            The size of the face after normalization.

        **Returns:**

        ``normbbx`` : 2D :py:class:`numpy.ndarray`
            Cropped facial image of the size (self.face_size, self.face_size).
        """

        cutframe = image[annotations['topleft'][0]:annotations['bottomright'][
            0], annotations['topleft'][1]:annotations['bottomright'][1]]

        tempbbx = np.ndarray((face_size, face_size), 'float64')
        normbbx = np.ndarray((face_size, face_size), 'uint8')
        bob.ip.base.scale(cutframe, tempbbx)  # normalization
        tempbbx_ = tempbbx + 0.5
        tempbbx_ = np.floor(tempbbx_)
        normbbx = np.cast['uint8'](tempbbx_)

        return normbbx

    #==========================================================================
    def crop_norm_faces_grayscale(self, images, annotations, face_size):
        """
        This function crops and normalizes faces in a stack of images given
        annotations of the face bounding box for the first image in the stack.

        **Parameters:**

        ``images`` : 3D :py:class:`numpy.ndarray`
            A stack of gray-scale input images. The size of the array is
            (n_images x n_rows x n_cols).

        ``annotations`` : :py:class:`dict`
            A dictionary containing annotations of the face bounding box.
            Dictionary must be as follows:
            ``{'topleft': (row, col), 'bottomright': (row, col)}``

        ``face_size`` : :py:class:`int`
            The size of the face after normalization.

        **Returns:**

        ``normbbx`` : 3D :py:class:`numpy.ndarray`
            A stack of normalized faces.
        """

        normbbx = []

        for image in images:

            normbbx.append(
                self.crop_norm_face_grayscale(image, annotations, face_size))

        normbbx = np.stack(normbbx)

        return normbbx

    #==========================================================================
    def select_all_blocks(self, images, block_size):
        """
        Extract all possible 3D blocks from a stack of images.

        ``images`` : 3D :py:class:`numpy.ndarray`
            A stack of gray-scale input images. The size of the array is
            (``n_images`` x ``n_rows`` x ``n_cols``).

        ``block_size`` : :py:class:`int`
            The spatial size of patches. The size of extracted 3D blocks is:
            (``n_images`` x ``block_size`` x ``block_size``).
        """

        (_, row_num, col_num) = images.shape

        all_blocks = []

        for row in range(row_num - block_size):

            for col in range(col_num - block_size):

                block = images[:, row:row + block_size, col:col + block_size]

                all_blocks.append(block)

        return all_blocks

    #==========================================================================
    def convert_frame_cont_to_grayscale_array(self, frame_cont):
        """
        Convert color video stored in the frame container into 3D array storing
        gray-scale frames. The dimensions of the output array are:
        (n_frames x n_rows x n_cols).

        **Parameters:**

        ``frames`` : FrameContainer
            Video data stored in the FrameContainer, see
            ``bob.bio.video.utils.FrameContainer`` for further details.

        **Returns:**

        ``result_array`` : 3D :py:class:`numpy.ndarray`
            A stack of gray-scale frames. The size of the array is
            (n_frames x n_rows x n_cols).
        """

        result_array = []

        for frame in frame_cont:

            image = frame[1]

            result_array.append(bob.ip.color.rgb_to_gray(image))

        result_array = np.stack(result_array)

        return result_array

    #==========================================================================
    def get_all_blocks_from_color_channel(self, video, annotations, block_size,
                                          block_length, min_face_size,
                                          norm_face_size):
        """
        Extract all 3D blocks from facial region of the input 3D array.
        Input 3D array represents one color channel of the video or a gray-scale
        video. Blocks are extracted from all 3D facial volumes. Facial volumes
        overlap with a shift of one frame.

        The size of the facial volume is:
        (``block_length`` x ``norm_face_size`` x ``norm_face_size``).

        The maximum number of available facial volumes in the video:
        (``num_of_frames_in_video`` - ``block_length``).
        However the final number of facial volumes might be less than above,
        because frames with small faces ( < min_face_size ) are discarded.

        **Parameters:**

        ``video`` : 3D :py:class:`numpy.ndarray`
            A stack of gray-scale input images. The size of the array is
            (n_images x n_rows x n_cols).

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure:
            ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``,
            where
            ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding
            box in frame N.

        ``block_size`` : :py:class:`int`
            The spatial size of facial patches.

        ``block_length`` : :py:class:`int`
            The temporal length of the stack of facial images / number of frames
            per stack.

        ``min_face_size`` : :py:class:`int`
            Discard frames with face of the size less than ``min_face_size``.

        ``norm_face_size`` : :py:class:`int`
            The size of the face after normalization.

        **Returns:**

        ``all_blocks`` : [[3D :py:class:`numpy.ndarray`]]
            Internal list contains all possible 3D blocks/volumes extracted from
            a particular stack of facial images. The dimensions of each 3D block:
            (block_length x block_size x block_size).
            The number of possible blocks is: (norm_face_size - block_size)^2.

            The length of the outer list is equal to the number of possible
            facial stacks in the input video:
            (``num_of_frames_in_video`` - ``block_length``).
            However, the final number of facial volumes might be less than above,
            because frames with small faces ( < min_face_size ) are discarded.
        """

        annotated_frames = annotations.keys()

        all_blocks = []

        for fn in range(len(video) - block_length):

            if str(fn) in annotated_frames:  # process if frame is annotated

                frame_annotations = annotations[str(fn)]

                face_size = np.min(
                    np.array(frame_annotations['bottomright']) -
                    np.array(frame_annotations['topleft']))

                if face_size >= min_face_size:  # process is face is large enough

                    # Selected 3D stacks of images. Stack has ``block_length`` images.
                    stack_of_images = video[fn:fn + block_length, :, :]

                    # 3D stacks of normalized face images.
                    faces = self.crop_norm_faces_grayscale(
                        stack_of_images, frame_annotations, norm_face_size)

                    # A list with all blocks per stack of facial images.
                    list_all_blocks_per_stack = self.select_all_blocks(
                        faces, block_size)

                    all_blocks.append(list_all_blocks_per_stack)

        return all_blocks

    #==========================================================================
    def extract_patches_from_blocks(self, all_blocks):
        """
        Extract frontal, central-horizontal and central-vertical patches from
        all blocks returned by ``get_all_blocks_from_color_channel``
        method of this class. The patches are returned in a vectorized form.

        **Parameters:**

        ``all_blocks`` : [[3D :py:class:`numpy.ndarray`]]
            Internal list contains all possible 3D blocks/volumes extracted from
            a particular stack of facial images. The dimensions of each 3D block:
            (block_length x block_size x block_size).
            The number of possible blocks is: (norm_face_size - block_size)^2.

            The length of the outer list is equal to the number of possible
            facial stacks in the input video:
            (``num_of_frames_in_video`` - ``block_length``).
            However, the final number of facial volumes might be less than above,
            because frames with small faces ( < min_face_size ) are discarded.

        **Returns:**

        ``frontal_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized frontal
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_size``^2 ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``horizontal_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized horizontal
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_length``*``block_size`` ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``vertical_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized vertical
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_length``*``block_size`` ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)
        """

        lenghth, row_num, col_num = all_blocks[0][0].shape

        selected_row = np.int(row_num / 2)

        selected_col = np.int(col_num / 2)

        frontal_patches = []
        horizontal_patches = []
        vertical_patches = []

        # volume - is a list of 3D blocks for a particular stack of facial images.
        for volume in all_blocks:

            volume_frontal_patches = []
            volume_horizontal_patches = []
            volume_vertical_patches = []

            for block in volume:

                frontal_patch = block[
                    0, :, :]  # the frontal patch of a block. Size: (row_num x col_num)
                volume_frontal_patches.append(frontal_patch.flatten())

                horizontal_patch = block[:,
                                         selected_row, :]  # the central-horizontal patch of a block. Size: (lenghth x col_num), where
                # lenghth = block_length, col_num = block_size.
                volume_horizontal_patches.append(horizontal_patch.flatten())

                vertical_patch = block[:, :,
                                       selected_col]  # the central-vertical patch of a block. Size: (lenghth x row_num)
                volume_vertical_patches.append(vertical_patch.flatten())

            frontal_patches.append(np.stack(volume_frontal_patches))

            horizontal_patches.append(np.stack(volume_horizontal_patches))

            vertical_patches.append(np.stack(volume_vertical_patches))

        return frontal_patches, horizontal_patches, vertical_patches

    #==========================================================================
    def __select_random_patches_single_list(self, patches, n_patches):
        """
        This method is called by ``select_random_patches`` method to process
        all lists of patches.

        **Parameters:**

        ``patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_size``^2 ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``n_patches`` : :py:class:`int`
            Number of randomly selected patches.

        **Returns:**

        ``selected_patches`` : [2D :py:class:`numpy.ndarray`]
            An array of selected patches. The dimensionality of the array:
            (``n_patches`` x ``number_of_features``).
        """

        all_patches = np.vstack(patches)

        idx = [
            random.randint(0,
                           len(all_patches) - 1) for _ in range(n_patches)
        ]

        selected_patches = all_patches[idx, :]

        return selected_patches

    #==========================================================================
    def select_random_patches(self, frontal_patches, horizontal_patches,
                              vertical_patches, n_patches):
        """
        Select random patches given lists of frontal, central-horizontal and
        central-vertical patches, as returned by ``extract_patches_from_blocks``
        method of this class.

        **Parameters:**

        ``frontal_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized frontal
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_size``^2 ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``horizontal_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized horizontal
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_length``*``block_size`` ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``vertical_patches`` : [2D :py:class:`numpy.ndarray`]
            Each element in the list contains an array of vectorized vertical
            patches for the particular stack of facial images.
            The size of each array is:
            ( (``norm_face_size`` - ``block_size``)^2 x ``block_length``*``block_size`` ).
            The maximum length of the list is:
            (``num_of_frames_in_video`` - ``block_length``)

        ``n_patches`` : :py:class:`int`
            Number of randomly selected patches.

        **Returns:**

        ``selected_frontal_patches`` : [2D :py:class:`numpy.ndarray`]
            An array of selected frontal patches.
            The dimensionality of the array:
            (``n_patches`` x ``number_of_features``).

        ``selected_horizontal_patches`` : [2D :py:class:`numpy.ndarray`]
            An array of selected horizontal patches.
            The dimensionality of the array:
            (``n_patches`` x ``number_of_features``).

        ``selected_vertical_patches`` : [2D :py:class:`numpy.ndarray`]
            An array of vertical selected patches.
            The dimensionality of the array:
            (``n_patches`` x ``number_of_features``).
        """

        selected_frontal_patches = self.__select_random_patches_single_list(
            frontal_patches, n_patches)

        selected_horizontal_patches = self.__select_random_patches_single_list(
            horizontal_patches, n_patches)

        selected_vertical_patches = self.__select_random_patches_single_list(
            vertical_patches, n_patches)

        return selected_frontal_patches, selected_horizontal_patches, selected_vertical_patches

    #==========================================================================
    def get_sparse_codes_for_patches(self, patches, dictionary):
        """
        This function computes a reconstruction sparse codes for a set of patches
        given dictionary to reconstruct the patches from. The OMP sparse coding
        algorithm is used for that.
        The maximum amount of non-zero entries in the sparse code is:
        ``num_of_features/5.``

        **Parameters:**

        ``patches`` : 2D :py:class:`numpy.ndarray`
            A vectorized patches to be reconstructed. The dimensionality is:
            (``n_samples`` x ``n_features``).

        ``dictionary`` : 2D :py:class:`numpy.ndarray`
            A dictionary to use for patch reconstruction. The dimensions are:
            (n_words_in_dictionary x n_features)

        **Returns:**

        ``codes`` : 2D :py:class:`numpy.ndarray`
            An array of reconstruction sparse codes for each patch.
            The dimensionality is:
            (``n_samples`` x ``n_words_in_the_dictionary``).
        """

        algo = 'omp'

        n_nonzero = np.int(dictionary.shape[1] / 5.)

        alpha = n_nonzero

        coder = SparseCoder(
            dictionary=dictionary,
            transform_n_nonzero_coefs=n_nonzero,
            transform_alpha=alpha,
            transform_algorithm=algo)

        # if a single patch is given of the shape (n_features,) convert it to the shape (1, n_features):

        if len(patches.shape) == 1:

            patches = patches.reshape(1, -1)

        codes = coder.transform(patches)

        return codes

    #==========================================================================
    def get_sparse_codes_for_list_of_patches(self, list_of_patches,
                                             dictionary):
        """
        Compute sparse codes for each array of vectorized patches in the list.
        This function just calls ``get_sparse_codes_for_patches`` method
        for each element of the input list.

        **Parameters:**

        ``patches`` : [2D :py:class:`numpy.ndarray`]
            A list of vectorized patches to be reconstructed.
            The dimensionality of each array in the list:
            (``n_samples`` x ``n_features``).

        ``dictionary`` : 2D :py:class:`numpy.ndarray`
            A dictionary to use for patch reconstruction. The dimensions are:
            (n_words_in_dictionary x n_features)

        **Returns:**

        ``video_codes`` : [2D :py:class:`numpy.ndarray`]
            A list of arrays with reconstruction sparse codes for each patch.
            The dimensionality of each array in the list is:
            (``n_samples`` x ``n_words_in_the_dictionary``).
        """

        video_codes = []

        for idx, patches in enumerate(list_of_patches):

            #            print idx

            codes = self.get_sparse_codes_for_patches(patches, dictionary)

            video_codes.append(codes)

        return video_codes

    #==========================================================================
    def load_array_from_hdf5(self, file_name):
        """
        Load an array from the hdf5 file given name of the file.

        **Parameters:**

        ``file_name`` : :py:class:`str`
            Name of the file.

        **Returns:**

        ``data`` : :py:class:`numpy.ndarray`
            Downloaded array.
        """

        f = bob.io.base.HDF5File(file_name)  #read only

        data = f.read('data')  #reads integer

        del f

        return data

    #==========================================================================
    def load_the_dictionaries(self, dictionary_file_names):
        """
        Download dictionaries, given names of the files containing them. The
        dictionaries are precomputed.

        **Parameters:**

        ``dictionary_file_names`` : [:py:class:`str`]
            A list of filenames containing the dictionary. The filenames must be
            listed in the following order:
            [file_name_pointing_to_frontal_dictionary,
            file_name_pointing_to_horizontal_dictionary,
            file_name_pointing_to_vertical_dictionary]

        **Returns:**

        ``dictionary_frontal`` : 2D :py:class:`numpy.ndarray`
            A dictionary to use for reconstruction of frontal patches.
            The dimensions are: (n_words_in_dictionary x n_features_front)

        ``dictionary_horizontal`` : 2D :py:class:`numpy.ndarray`
            A dictionary to use for reconstruction of horizontal patches.
            The dimensions are: (n_words_in_dictionary x n_features_horizont)

        ``dictionary_vertical`` : 2D :py:class:`numpy.ndarray`
            A dictionary to use for reconstruction of vertical patches.
            The dimensions are: (n_words_in_dictionary x n_features_vert)
        """

        dictionary_frontal = self.load_array_from_hdf5(
            dictionary_file_names[0])

        dictionary_horizontal = self.load_array_from_hdf5(
            dictionary_file_names[1])

        dictionary_vertical = self.load_array_from_hdf5(
            dictionary_file_names[2])

        return dictionary_frontal, dictionary_horizontal, dictionary_vertical

    #==========================================================================
    def convert_sparse_codes_to_frame_container(self, sparse_codes):
        """
        Convert an input list of lists of 2D arrays / sparse codes into Frame
        Container. Each frame in the output Frame Container is a 3D array which
        stacks 3 2D arrays representing particular frame / stack of facial images.

        **Parameters:**

        ``sparse_codes`` : [[2D :py:class:`numpy.ndarray`]]
            A list of lists of 2D arrays. Each 2D array contains sparse codes
            of a particular stack of facial images. The length of internal lists
            is equal to the number of processed frames. The outer list contains
            the codes for frontal, horizontal and vertical patches, thus the
            length of an outer list in the context of this class is 3.

        **Returns:**

        ``frame_container`` : FrameContainer
            FrameContainer containing the frames with sparse codes for the
            frontal, horizontal and vertical patches. Each frame is a 3D array.
            The dimensionality of array is:
            (``3`` x ``n_samples`` x ``n_words_in_the_dictionary``).
        """

        frame_container = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        idx = 0

        for frontal_codes, horizontal_codes, vertical_codes in zip(
                sparse_codes[0], sparse_codes[1], sparse_codes[2]):

            frame_3d = np.stack(
                [frontal_codes, horizontal_codes, vertical_codes])

            frame_container.add(idx, frame_3d)  # add frame to FrameContainer

            idx = idx + 1

        return frame_container

    #==========================================================================
    def comp_hist_of_sparse_codes(self, sparse_codes, method):
        """
        Compute the histograms of sparse codes.

        **Parameters:**

        ``sparse_codes`` : [[2D :py:class:`numpy.ndarray`]]
            A list of lists of 2D arrays. Each 2D array contains sparse codes
            of a particular stack of facial images. The length of internal lists
            is equal to the number of processed frames. The outer list contains
            the codes for frontal, horizontal and vertical patches, thus the
            length of an outer list in the context of this class is 3.

        ``method`` : :py:class:`str`
            Name of the method to be used for combining the sparse codes into
            a single feature vector. Two options are possible: "mean" and
            "hist". If "mean" is selected the mean for ``n_samples`` dimension
            is first computed. The resulting vectors for various types of
            patches are then concatenated into a single feature vector.
            If "hist" is selected, the values in the input array are first
            binarized setting all non-zero elements to one. The rest of the
            process is similar to the "mean" combination method.

        **Returns:**

        ``frame_container`` : FrameContainer
            FrameContainer containing the frames with sparse codes for the
            frontal, horizontal and vertical patches. Each frame is a 3D array.
            The dimensionality of array is:
            (``3`` x ``n_samples`` x ``n_words_in_the_dictionary``).
        """

        histograms = []

        for frontal_codes, horizontal_codes, vertical_codes in zip(
                sparse_codes[0], sparse_codes[1], sparse_codes[2]):

            frame = np.stack([frontal_codes, horizontal_codes, vertical_codes])

            if method == "mean":

                frame_codes = np.mean(frame, axis=1)

            if method == "hist":

                frame_codes = np.mean(frame != 0, axis=1)

            for idx, row in enumerate(frame_codes):

                frame_codes[idx, :] = row / np.sum(row)

            hist = frame_codes.flatten()

            histograms.append(hist)

        return histograms

    #==========================================================================
    def convert_arrays_to_frame_container(self, list_of_arrays):
        """
        Convert an input list of arrays into Frame Container.

        **Parameters:**

        ``list_of_arrays`` : [:py:class:`numpy.ndarray`]
            A list of arrays.

        **Returns:**

        ``frame_container`` : FrameContainer
            FrameContainer containing the feature vectors.
        """

        frame_container = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        for idx, item in enumerate(list_of_arrays):

            frame_container.add(idx, item)  # add frame to FrameContainer

        return frame_container

    #==========================================================================
    def mean_std_normalize(self,
                           features,
                           features_mean=None,
                           features_std=None):
        """
        The features in the input 2D array are mean-std normalized.
        The rows are samples, the columns are features. If ``features_mean``
        and ``features_std`` are provided, then these vectors will be used for
        normalization. Otherwise, the mean and std of the features is
        computed on the fly.

        **Parameters:**

        ``features`` : 2D :py:class:`numpy.ndarray`
            Array of features to be normalized.

        ``features_mean`` : 1D :py:class:`numpy.ndarray`
            Mean of the features. Default: None.

        ``features_std`` : 2D :py:class:`numpy.ndarray`
            Standart deviation of the features. Default: None.

        **Returns:**

        ``features_norm`` : 2D :py:class:`numpy.ndarray`
            Normalized array of features.

        ``features_mean`` : 1D :py:class:`numpy.ndarray`
            Mean of the features.

        ``features_std`` : 1D :py:class:`numpy.ndarray`
            Standart deviation of the features.
        """

        features = np.copy(features)

        # Compute mean and std if not given:
        if features_mean is None:

            features_mean = np.mean(features, axis=0)

            features_std = np.std(features, axis=0)

        row_norm_list = []

        for row in features:  # row is a sample

            row_norm = (row - features_mean) / features_std

            row_norm_list.append(row_norm)

        features_norm = np.vstack(row_norm_list)

        return features_norm, features_mean, features_std

    #==========================================================================
    def compute_patches_mean_squared_errors(self, sparse_codes, original_data,
                                            dictionary):
        """
        This function computes normalized mean squared errors (MSE) for each
        feature (column) in the reconstructed array of vectorized patches.
        The patches are reconstructed given array of sparse codes and a dictionary.

        **Parameters:**

        ``sparse_codes`` : 2D :py:class:`numpy.ndarray`
            An array of sparse codes. Each row contains a sparse code encoding a
            vectorized patch. The dimensionality of the array:
            (``n_samples`` x ``n_words_in_dictionary``).

        ``original_data`` : 2D :py:class:`numpy.ndarray`
            An array with original vectorized patches.
            The dimensionality of the array:
            (``n_samples`` x ``n_features_in_patch``).

        ``dictionary`` : 2D :py:class:`numpy.ndarray`
            A dictionary with vectorized visual words.
            The dimensionality of the array:
            (``n_words_in_dictionary`` x ``n_features_in_patch``).

        **Returns:**

        ``squared_errors`` : 1D :py:class:`numpy.ndarray`
            Normalzied MSE for each feature across all patches/samples.
            The dimensionality of the array:
            (``n_features_in_patch``, ).
        """

        recovered_data = np.dot(sparse_codes, dictionary)

        squared_error = 1. * np.sum(
            (original_data - recovered_data)**2, axis=0) / np.sum(
                original_data**2, axis=0)

        return squared_error

    #==========================================================================
    def compute_mse_for_all_patches_types(self, sparse_codes_list,
                                          original_data_list, dictionary_list):
        """
        This function computes mean squared errors (MSE) for all types of patches:
        frontal, horizontal, and vertical. In this case the function
        ``compute_patches_mean_squared_errors`` is called in a loop for all
        values in the input lists.

        **Parameters:**

        ``sparse_codes_list`` : [2D :py:class:`numpy.ndarray`]
            A list with arrays of sparse codes. Each row in the arrays contains a
            sparse code encoding a vectorized patch of particular type.
            The dimensionality of the each array:
            (``n_samples`` x ``n_words_in_dictionary``).

        ``original_data_list`` : [2D :py:class:`numpy.ndarray`]
            A list of arrays with original vectorized patches of various types.
            The dimensionality of the arrays might be different for various types
            of the patches:
            (``n_samples`` x ``n_features_in_patch_of_particular_type``).

        ``dictionary_list`` : [2D :py:class:`numpy.ndarray`]
            A list of dictionaries with vectorized visual words of various types.
            The dimensionality of the arrays might be different for various types
            of the patches:
            (``n_words_in_dictionary`` x ``n_features_in_patch_of_particular_type``).

        **Returns:**

        ``squared_errors`` : 2D :py:class:`numpy.ndarray`
            First row:
            MSE of features for various types of patches concatenated into a single
            vector.
            Second row:
            The same as above but MSE are sorted for each type of patches.
            The dimensionality of the array:
            (2 x ``n_features_in_patch_of_all_types``).
        """

        squared_errors = []

        squared_errors_sorted = []

        for sparse_codes, original_data, dictionary in zip(
                sparse_codes_list, original_data_list, dictionary_list):

            squared_error = self.compute_patches_mean_squared_errors(
                sparse_codes, original_data, dictionary)

            squared_error_sorted = np.sort(squared_error)

            squared_errors.append(squared_error)

            squared_errors_sorted.append(squared_error_sorted)

        squared_errors = np.hstack(squared_errors)

        squared_errors_sorted = np.hstack(squared_errors_sorted)

        squared_errors = np.vstack([squared_errors, squared_errors_sorted])

        return squared_errors

    #==========================================================================
    def compute_mse_for_all_stacks(self, video_codes_list, patches_list,
                                   dictionary_list):
        """
        Call ``compute_mse_for_all_patches_types`` for data coming from all stacks
        of facial images.

        **Parameters:**

        ``video_codes_list`` : [ [2D :py:class:`numpy.ndarray`] ]
            A list with ``frontal_video_codes``, ``horizontal_video_codes``, and
            ``vertical_video_codes`` as returned by ``get_sparse_codes_for_list_of_patches``
            method of this class.

        ``patches_list`` : [ [2D :py:class:`numpy.ndarray`] ]
            A list with ``frontal_patches``, ``horizontal_patches``, and
            ``vertical_patches`` as returned by ``extract_patches_from_blocks``
            method of this class.

        ``dictionary_list`` : [2D :py:class:`numpy.ndarray`]
            A list of dictionaries with vectorized visual words of various types.
            The dimensionality of the arrays might be different for various types
            of the patches:
            (``n_words_in_dictionary`` x ``n_features_in_patch_of_particular_type``).

        **Returns:**

        ``squared_errors_list`` : [2D :py:class:`numpy.ndarray`]
            A list of ``squared_errors`` as returned by ``compute_mse_for_all_patches_types``
            method of this class.
        """

        fcs = video_codes_list[0]
        hcs = video_codes_list[1]
        vcs = video_codes_list[2]

        fps = patches_list[0]
        hps = patches_list[1]
        vps = patches_list[2]

        squared_errors_list = []

        for fc, hc, vc, fp, hp, vp in zip(fcs, hcs, vcs, fps, hps, vps):

            sparse_codes_list = [fc, hc, vc]

            original_data_list = [fp, hp, vp]

            squared_errors = self.compute_mse_for_all_patches_types(
                sparse_codes_list, original_data_list, dictionary_list)

            squared_errors_list.append(squared_errors)

        return squared_errors_list

    #==========================================================================
    def __call__(self, frames, annotations):
        """
        Compute sparse codes for spatial frontal, spatio-temporal horizontal,
        and spatio-temporal vertical patches. The codes are computed for all
        possible stacks of facial images. The maximum possible number of stacks
        is: (``num_of_frames_in_video`` - ``block_length``).
        However, this number can be smaller, and is controlled by two arguments
        of this class: ``min_face_size`` and ``frame_step``.

        If ``self.extract_histograms_flag`` flag is set to ``True`` the
        histograms of sparse codes will be computed for all possible stacks of
        facial images.

        **Parameters:**

        ``frames`` : FrameContainer
            Video data stored in the FrameContainer, see
            ``bob.bio.video.utils.FrameContainer`` for further details.

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure:
            ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``,
            where
            ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding
            box in frame N.

        **Returns:**

        ``frame_container`` : FrameContainer
            If ``self.extract_histograms_flag`` flag is set to ``False`:
            FrameContainer containing the frames with sparse codes for the
            frontal, horizontal and vertical patches. Each frame is a 3D array.
            The dimensionality of each array is:
            (``3`` x ``n_samples`` x ``n_words_in_the_dictionary``).
            The first slice in the 3D arrays corresponds to frontal sparse codes,
            second slice to horizontal, and third to vertical codes.

            If ``self.extract_histograms_flag`` flag is set to ``True`` the
            histograms of sparse codes will be computed. In this case each
            frame is a 1D array with dimensionality:
            (3*``n_words_in_the_dictionary``, )
        """

        # Convert frame container to 3D array:
        video = self.convert_frame_cont_to_grayscale_array(frames)

        # Get all blocks from all possible facial stacks:
        all_blocks = self.get_all_blocks_from_color_channel(
            video, annotations, self.block_size, self.block_length,
            self.min_face_size, self.norm_face_size)

        # Extract three sets of patches per each stack of facial images:
        frontal_patches, horizontal_patches, vertical_patches = self.extract_patches_from_blocks(
            all_blocks)

        # Download the dictionaries:
        dictionary_frontal, dictionary_horizontal, dictionary_vertical = self.load_the_dictionaries(
            self.dictionary_file_names)

        # Select subset of patches if ``frame_step`` > 1:
        frontal_patches_subset = frontal_patches[::self.frame_step]
        horizontal_patches_subset = horizontal_patches[::self.frame_step]
        vertical_patches_subset = vertical_patches[::self.frame_step]

        # Compute sparse codes for all patches of all types:
        frontal_video_codes = self.get_sparse_codes_for_list_of_patches(
            frontal_patches_subset, dictionary_frontal)
        horizontal_video_codes = self.get_sparse_codes_for_list_of_patches(
            horizontal_patches_subset, dictionary_horizontal)
        vertical_video_codes = self.get_sparse_codes_for_list_of_patches(
            vertical_patches_subset, dictionary_vertical)

        if self.comp_reconstruct_err_flag:

            video_codes_list = [
                frontal_video_codes, horizontal_video_codes,
                vertical_video_codes
            ]

            patches_list = [
                frontal_patches_subset, horizontal_patches_subset,
                vertical_patches_subset
            ]

            dictionary_list = [
                dictionary_frontal, dictionary_horizontal, dictionary_vertical
            ]

            squared_errors_list = self.compute_mse_for_all_stacks(
                video_codes_list, patches_list, dictionary_list)

            frame_container = self.convert_arrays_to_frame_container(
                squared_errors_list)

        else:

            if self.extract_histograms_flag:  # in this case histograms will be extracted in the preprocessor , no feature extraction is needed then

                histograms = self.comp_hist_of_sparse_codes([
                    frontal_video_codes, horizontal_video_codes,
                    vertical_video_codes
                ], self.method)

                frame_container = self.convert_arrays_to_frame_container(
                    histograms)

            else:

                frame_container = self.convert_sparse_codes_to_frame_container(
                    [
                        frontal_video_codes, horizontal_video_codes,
                        vertical_video_codes
                    ])

        return frame_container

    #==========================================================================
    def write_data(self, frames, file_name):
        """
        Writes the given data (that has been generated using the __call__
        function of this class) to file. This method overwrites the write_data()
        method of the Preprocessor class.

        **Parameters:**

        ``frames`` :
            data returned by the __call__ method of the class.

        ``file_name`` : :py:class:`str`
            name of the file.
        """

        self.video_preprocessor.write_data(frames, file_name)

    #==========================================================================
    def read_data(self, file_name):
        """
        Reads the preprocessed data from file.
        This method overwrites the read_data() method of the Preprocessor class.

        **Parameters:**

        ``file_name`` : :py:class:`str`
            name of the file.

        **Returns:**

        ``frames`` : :py:class:`bob.bio.video.FrameContainer`
            Frames stored in the frame container.
        """

        frames = self.video_preprocessor.read_data(file_name)

        return frames
