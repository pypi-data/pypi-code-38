import numpy as np

from scipy import stats
from scipy.ndimage.morphology import distance_transform_edt
from skimage.morphology import skeletonize_3d

from mahotas.features import haralick

from scipy.ndimage.morphology import distance_transform_edt as bwdist
from skimage.transform import resize

import warnings


def get_simple_binary_image():
    warnings.warn("This function is depricated in favor of common.get_simple_image()")
    # Returns a simple 10x10x10 binary image

    img = np.zeros((10, 10, 10), dtype=np.uint16)
    img[4:7, 4:7, 4:7] = 1

    return img


def get_simple_image(im_size=np.array([201, 201, 201]), return2D=False):
    """
        :get_simple_image:
        Returns a simple "cell" image, where the cell and nuclear shapes are a sphere within a sphere,
        with the structure channel being a sphere that is the same as the cell shape. Segmentations
        are binary versions of the images.

        :return:
        im_cell = uint16 numpy array that is a big sphere
        im_nuc = uint16 numpy array that is a small sphere inside of im_cell
        im_struct = same as im_cell
        seg_cell = same as im_cell but binary
        seg_nuc = same as im_nuc but binary
        seg_struct = same as im_struct but binary
    """

    im_start = np.array([101, 101, 101])

    centroid = ((im_start[0] - 1) / 2).astype("int")

    im_bounding_box = np.ones(im_size)
    im_bounding_box[centroid, centroid, centroid] = 0
    im_dist = bwdist(im_bounding_box)
    im_dist = resize(im_dist, im_size, order=0)

    im_cell = im_dist <= (centroid - 2)

    im_nuc = im_dist <= np.percentile(im_dist[im_cell], 50)

    if return2D:
        im_cell = np.expand_dims(np.max(im_cell, 0), 0)
        im_nuc = np.expand_dims(np.max(im_nuc, 0), 0)

    im_struct = im_cell.copy()

    im_cell = im_cell.astype("uint16")
    im_nuc = im_nuc.astype("uint16")
    im_struct = im_struct.astype("uint16")

    seg_cell = im_cell.copy() > 0
    seg_nuc = im_nuc.copy() > 0
    seg_struct = im_struct.copy() > 0

    return im_cell, im_nuc, im_struct, seg_cell, seg_nuc, seg_struct


def get_shape_features(seg):

    """
        :param seg: 3D binary image containing a single connected
        component. Background has value 0 and object of interest
        has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(seg.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(seg.shape))

    # Calculates the volume as the total number of non-zero voxels.

    features["volume"] = np.count_nonzero(seg)

    # Calculates the surface area as the total number of voxels at
    # distance 1 from the object of interest.

    dist_trans = distance_transform_edt(seg > 0)

    features["surface_area"] = np.count_nonzero(dist_trans == 1)

    # Calculates the axes features from the covariance matrix of the
    # voxels coordinates. Results are returned in descending order of
    # eigenvalue.

    z_pxl, y_pxl, x_pxl = np.where(seg > 0)

    number_of_voxels = len(z_pxl)

    axs = []
    axs_length = []

    if number_of_voxels:

        xyz_pxl_table = np.concatenate(
            [x_pxl.reshape(-1, 1), y_pxl.reshape(-1, 1), z_pxl.reshape(-1, 1)], axis=1
        )

        eigenvals, eigenvecs = np.linalg.eig(np.cov(xyz_pxl_table.transpose()))

        idx = eigenvals.argsort()
        eigenvals = eigenvals[idx]
        eigenvecs = eigenvecs[:, idx]

        for i in range(3):
            vec = eigenvecs[:, -1 - i]
            ptp = np.inner(vec, xyz_pxl_table)
            axs_length.append(np.ptp(ptp))
            axs.append(vec)

        meridional_eccentricity = (
            np.nan
            if np.abs(eigenvals[2]) < 1e-12
            else np.sqrt(1 - np.square(eigenvals[0] / eigenvals[2]))
        )
        equator_eccentricity = (
            np.nan
            if np.abs(eigenvals[1]) < 1e-12
            else np.sqrt(1 - np.square(eigenvals[0] / eigenvals[1]))
        )

    if number_of_voxels == 0:

        features["shape_1st_axis_x"] = np.nan
        features["shape_1st_axis_y"] = np.nan
        features["shape_1st_axis_z"] = np.nan
        features["shape_2nd_axis_x"] = np.nan
        features["shape_2nd_axis_y"] = np.nan
        features["shape_2nd_axis_z"] = np.nan
        features["shape_3rd_axis_x"] = np.nan
        features["shape_3rd_axis_y"] = np.nan
        features["shape_3rd_axis_z"] = np.nan
        features["shape_1st_axis_length"] = np.nan
        features["shape_2nd_axis_length"] = np.nan
        features["shape_3rd_axis_length"] = np.nan
        features["shape_1st_eigenvalue"] = np.nan
        features["shape_2nd_eigenvalue"] = np.nan
        features["shape_3rd_eigenvalue"] = np.nan
        features["shape_meridional_eccentricity"] = np.nan
        features["shape_equator_eccentricity"] = np.nan

    else:

        features["shape_1st_axis_x"] = axs[0][0]
        features["shape_1st_axis_y"] = axs[0][1]
        features["shape_1st_axis_z"] = axs[0][2]
        features["shape_2nd_axis_x"] = axs[1][0]
        features["shape_2nd_axis_y"] = axs[1][1]
        features["shape_2nd_axis_z"] = axs[1][2]
        features["shape_3rd_axis_x"] = axs[2][0]
        features["shape_3rd_axis_y"] = axs[2][1]
        features["shape_3rd_axis_z"] = axs[2][2]
        features["shape_1st_axis_length"] = axs_length[0]
        features["shape_2nd_axis_length"] = axs_length[1]
        features["shape_3rd_axis_length"] = axs_length[2]
        features["shape_1st_eigenvalue"] = eigenvals[0]
        features["shape_2nd_eigenvalue"] = eigenvals[1]
        features["shape_3rd_eigenvalue"] = eigenvals[2]
        features["shape_meridional_eccentricity"] = meridional_eccentricity
        features["shape_equator_eccentricity"] = equator_eccentricity

    # Calculates the sphericity that represents how closely the shape of the
    # object of interest approaches that of a mathematically perfect sphere.

    if features["surface_area"] == 0:

        features["shape_sphericity"] = np.nan

    else:

        features["shape_sphericity"] = (
            np.power(np.pi, 1.0 / 3)
            * np.power(6 * features["volume"], 2.0 / 3)
            / features["surface_area"]
        )

    return features


def get_position_features(seg):

    """
        :param seg: 3D binary image containing a single connected
        component. Background has value 0 and object of interest
        has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(seg.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(seg.shape))

    z_pxl, y_pxl, x_pxl = np.nonzero(seg)

    number_of_voxels = len(z_pxl)

    if number_of_voxels > 0:

        features["position_lowest_z"] = np.min(z_pxl)
        features["position_highest_z"] = np.max(z_pxl)
        features["position_x_centroid"] = np.mean(x_pxl)
        features["position_y_centroid"] = np.mean(y_pxl)
        features["position_z_centroid"] = np.mean(z_pxl)

    else:

        features["position_lowest_z"] = np.nan
        features["position_highest_z"] = np.nan
        features["position_x_centroid"] = np.nan
        features["position_y_centroid"] = np.nan
        features["position_z_centroid"] = np.nan

    return features


def get_intensity_features(img):

    """
        :param seg: 3D 16-bit image (usually given by a multiplication
        of a gray scale image and its segmented version). The images
        contains a single connected component. Background has value 0
        and object of interest has value > 0.

        :return: df - dictionary of features
    """

    if len(img.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(img.shape))

    features = {}

    # Pixel intensity moments and basic related statistics

    pxl_valids = np.nonzero(img)

    number_of_voxels = len(pxl_valids[0])

    if number_of_voxels > 0:

        features["intensity_mean"] = np.mean(img[pxl_valids])

        features["intensity_median"] = np.median(img[pxl_valids])

        features["intensity_sum"] = np.sum(img[pxl_valids])

        features["intensity_mode"] = stats.mode(img[pxl_valids])[0][0]

        features["intensity_max"] = np.max(img[pxl_valids])

        features["intensity_std"] = np.std(img[pxl_valids])

        # Intensity entropy

        prob = np.bincount(img[pxl_valids], minlength=65535)
        features["intensity_entropy"] = stats.entropy(prob / number_of_voxels)

    else:

        features["intensity_mean"] = np.nan
        features["intensity_median"] = np.nan
        features["intensity_sum"] = np.nan
        features["intensity_mode"] = np.nan
        features["intensity_max"] = np.nan
        features["intensity_std"] = np.nan
        features["intensity_entropy"] = np.nan

    return features


def get_texture_features(img, scaling_params=[0.5, 18]):

    """
        :param seg: 3D 16-bit image (usually given by a multiplication
        of a gray scale image and its segmented version). The images
        contains a single connected component. Background has value 0
        and object of interest has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(img.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(img.shape))

    pxl_valids = np.nonzero(img)

    number_of_voxels = len(pxl_valids[0])

    # Haralick texture features as decribed in [1]. See [2] for original paper by Haralick et. al
    # [1] - https://mahotas.readthedocs.io/en/latest/api.html?highlight=mahotas.features.haralick
    # [2] - Haralick et. al. Textural features for image classification. IEEE Transactions on systems, man, and cybernetics, (6), 610-621.
    # Notice that a minimal number of pixels (512) is required for computing these features.

    number_of_voxels_required = 512

    if number_of_voxels >= number_of_voxels_required:

        # if secretly a 2D image
        if img.shape[0] == 1:
            img = np.squeeze(img, 0)

        ftextural = haralick(img, ignore_zeros=True, return_mean=True)

    for fid, fname in enumerate(
        [
            "texture_haralick_ang2nd_moment",
            "texture_haralick_contrast",
            "texture_haralick_corr",
            "texture_haralick_variance",
            "texture_haralick_inv_diff_moment",
            "texture_haralick_sum_avg",
            "texture_haralick_sum_var",
            "texture_haralick_sum_entropy",
            "texture_haralick_entropy",
            "texture_haralick_diff_var",
            "texture_haralick_diff_entropy",
            "texture_haralick_info_corr1",
            "texture_haralick_info_corr2",
        ]
    ):
        features[fname] = (
            np.nan if number_of_voxels <= number_of_voxels_required else ftextural[fid]
        )

    return features


def get_skeleton_features(seg):

    """
        :param seg: 3D 16-bit image (usually given by a multiplication
        of a gray scale image and its segmented version). The images
        contains a single connected component. Background has value 0
        and object of interest has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(seg.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(seg.shape))

    # 3D skeletonization from scikit image

    skel = skeletonize_3d(seg.astype(np.uint8))

    skel[skel > 0] = 1

    skel = np.pad(skel, 1, "constant")

    skel_degree = np.copy(skel)

    # Creating an image where the value of each pixel represents
    # its number of neighbors after skeletonization.

    z_pxl, y_pxl, x_pxl = np.where(skel > 0)

    nv = len(z_pxl)

    for x, y, z in zip(x_pxl, y_pxl, z_pxl):
        neigh = skel[z - 1 : z + 2, y - 1 : y + 2, x - 1 : x + 2]  # noqa
        skel_degree[z, y, x] = neigh.sum()

    nt = skel.sum()
    n0 = np.sum(skel_degree == (0 + 1))
    n1 = np.sum(skel_degree == (1 + 1))
    n2 = np.sum(skel_degree == (2 + 1))
    n3 = np.sum(skel_degree == (3 + 1))
    n4 = np.sum(skel_degree >= (4 + 1))

    # Average degree from <k> = Σ k x Pk

    if n2 != nt:
        average_degree = 0
        deg, Ndeg = np.unique(skel_degree.reshape(-1), return_counts=True)
        for k, n in zip(deg, Ndeg):
            if k != 2:
                average_degree = average_degree + k * (n / (nt - n2))
    else:
        average_degree = 1

    features["skeleton_voxels_number"] = nt
    features["skeleton_nodes_number"] = nt - n2
    features["skeleton_degree_mean"] = average_degree
    features["skeleton_edges_number"] = np.int(0.5 * (nt - n2) * average_degree)

    # Every pixel has to have at least one neighbor if the skeleton
    # contains more than a single pixel.

    if nt > 1:
        assert n0 == 0

    # Reminder: in the case of components that represent closed loops,
    # may only contain nodes with degree two. For sake of simplicity we
    # treat these single looped components as containing a single node
    # with degree one.

    features["skeleton_deg0_prop"] = (
        np.nan if nv == 0 else 0.0 if n2 == nt else n0 / (1.0 * nt - n2)
    )
    features["skeleton_deg1_prop"] = (
        np.nan if nv == 0 else 1.0 if n2 == nt else n1 / (1.0 * nt - n2)
    )
    features["skeleton_deg3_prop"] = (
        np.nan if nv == 0 else 0.0 if n2 == nt else n3 / (1.0 * nt - n2)
    )
    features["skeleton_deg4p_prop"] = (
        np.nan if nv == 0 else 0.0 if n2 == nt else n4 / (1.0 * nt - n2)
    )

    return features


def get_io_intensity_features(img, number_ops=1):

    """
        Applies erosion operation "number_ops" times
        to divide the image into two regions, called
        outer and inner regions. If the object is a
        sphere of readius R, the outer region will be
        a shell with width number_ops and the inner
        region will be a smaller sphere of radius
        R-number_ops.

        :param seg: 3D 16-bit image (usually given by a multiplication
        of a gray scale image and its segmented version). The images
        contains a single connected component. Background has value 0
        and object of interest has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(img.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(img.shape))

    from skimage.morphology import binary_erosion

    img_bin = img.copy()
    img_bin[img_bin > 0] = 1

    z_pxl, y_pxl, x_pxl = np.where(img_bin > 0)

    # Sequence of erosion to create inner and outer images

    img_inner = img_bin.copy()
    img_outer = img_bin.copy()
    for op in range(number_ops):
        img_inner = binary_erosion(img_inner)
    img_outer = img_outer - img_inner

    number_of_voxels_inner = img_inner.sum()
    number_of_voxels_outer = img_outer.sum()

    # Multiply binary with input to retrieve original intensity

    img_inner = img_inner * img
    img_outer = img_outer * img

    img_inner = img_inner.reshape(-1)
    img_outer = img_outer.reshape(-1)

    # Keep only non zero values

    img_inner = img_inner[img_inner > 0]
    img_outer = img_outer[img_outer > 0]

    features["io_intensity_volume_inner"] = number_of_voxels_inner
    features["io_intensity_volume_outer"] = number_of_voxels_outer
    features["io_intensity_outer_mean"] = img_outer.mean()
    features["io_intensity_outer_std"] = img_outer.std()

    if number_of_voxels_inner > 0:

        features["io_intensity_inner_mean"] = img_inner.mean()
        features["io_intensity_inner_std"] = img_inner.std()

    else:

        features["io_intensity_inner_mean"] = np.nan
        features["io_intensity_inner_std"] = np.nan

    return features


def get_bright_spots_features(img):

    """
        Uses extrema.h_maxima from skimage.morphology
        to identify bright spots in the input image.
        After detection, a region around each maxima
        is cropped to create an average spot from which
        measurements are taken.

        :param seg: 3D 16-bit image (usually given by a multiplication
        of a gray scale image and its segmented version). The images
        contains a single connected component. Background has value 0
        and object of interest has value > 0.

        :return: df - dictionary of features
    """

    features = {}

    if len(img.shape) != 3:
        raise ValueError("Incorrect dimensions: {}".format(img.shape))

    from skimage.filters import gaussian
    from skimage.morphology import extrema, binary_dilation

    def norm_and_smooth(img_original, smooth_sigma=1.0, scaling_params=[0.5, 18]):

        # Uses Jianxu's normalization and Gaussian smooth to
        # preprocess the input image. Parameters have default
        # values used in the segmentation toolkit.
        img_norm = img_original.copy()
        mean = img_norm.mean()
        stdv = img_norm.std()
        strech_min = np.max([mean - scaling_params[0] * stdv, img_norm.min()])
        strech_max = np.min([mean + scaling_params[1] * stdv, img_norm.max()])
        img_norm[img_norm > strech_max] = strech_max
        img_norm[img_norm < strech_min] = strech_min
        img_norm = (img_norm - strech_min + 1e-8) / (strech_max - strech_min + 1e-8)
        img_norm = gaussian(image=img_norm, sigma=smooth_sigma)

        # img_norm may contain negative values

        return img_norm

    img_norm = norm_and_smooth(img_original=img)

    # Find maxima

    img_max = extrema.h_maxima(img_norm, h=0.1)
    z_pxl, y_pxl, x_pxl = np.nonzero(img_max)

    number_of_maxima = len(x_pxl)

    # Calculates the average intensity of maxima.

    img_max = binary_dilation(img_max)

    maxima_mean_intensity = img[img_max > 0].mean()

    # Radius of the region cropped around each maxima. Final
    # patch will have size 2r+1  x 2r+1 x 3. Z direction is
    # not resampled.

    r = 11

    # For each maxima we crop a region and append their max
    # projection

    spots = []
    for n_id in range(number_of_maxima):
        x = x_pxl[n_id]
        y = y_pxl[n_id]
        z = z_pxl[n_id]
        if np.min([r, x, y, img.shape[2] - x, img.shape[1] - y]) == r:
            img_crop = img[
                (z - 2) : (z + 3), (y - r) : (y + r + 1), (x - r) : (x + r + 1)  # noqa
            ]
            spots.append(img_crop.max(axis=0))
            img_norm[z, (y - 1) : (y + 2), (x - 1) : (x + 2)] = 1  # noqa
    spots = np.array(spots)
    spots.reshape(-1, 2 * r + 1, 2 * r + 1)

    # Calculates the mean std of the average region

    avg_spot = spots.mean(axis=0)
    avg_spot = avg_spot - avg_spot.min()
    prob_x = avg_spot.sum(axis=1) / avg_spot.sum()
    prob_y = avg_spot.sum(axis=0) / avg_spot.sum()
    s = np.linspace(start=-r, stop=r, num=2 * r + 1)
    std_x = np.sqrt(((s ** 2) * prob_x).sum())
    std_y = np.sqrt(((s ** 2) * prob_y).sum())

    std = np.mean([std_x, std_y])

    # Need to document this feature and test. Also, add number of
    # spots as feature and their intensity

    features["bright_spots_number"] = number_of_maxima

    if number_of_maxima > 0:

        features["bright_spots_intensity_mean"] = maxima_mean_intensity

        features["bright_spots_width"] = std

    else:

        features["bright_spots_intensity_mean"] = np.nan

        features["bright_spots_width"] = np.nan

    return features
