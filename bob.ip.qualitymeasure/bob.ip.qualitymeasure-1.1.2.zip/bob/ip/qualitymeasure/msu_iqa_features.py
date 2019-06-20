#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


import numpy as np
import scipy.signal as ssg
import bob.ip.base
import bob.ip.color
from . import galbally_iqm_features as iqm

from . import remove_highlights

''' Utility functions '''

def matlab_rgb2hsv(rgbImage):
    # first normalize the range of values to 0-1

    isUint8 = True
    if isUint8:
        rgbImage = rgbImage.astype(np.float64) / 255.0

    hsv = np.zeros_like(rgbImage)
    bob.ip.color.rgb_to_hsv(rgbImage, hsv)
    h = hsv[0, :, :]
    s = hsv[1, :, :]
    v = hsv[2, :, :]

    return (h, s, v)


def imshow(image):
    import matplotlib
    from matplotlib import pyplot as plt
    if len(image.shape) == 3:
        # imshow() expects color image in a slightly different format, so first
        # rearrange the 3d data for imshow...
        outImg = image.tolist()
        print(len(outImg))
        result = np.dstack((outImg[0], outImg[1]))
        outImg = np.dstack((result, outImg[2]))
        # [:,:,1], cmap=mpl.cm.gray)
        plt.imshow((outImg * 255.0).astype(np.uint8))

    else:
        if(len(image.shape) == 2):
            # display gray image.
            plt.imshow(image.astype(np.uint8), cmap=matplotlib.cm.gray)

    plt.show()


'''Auxilliary functions'''


def sobelEdgeMap(image, orientation='both'):

    # bob..sobel returns filter-responses which need to be thresholded to get
    # the edge-map
    thinning = 1
    refImage = image.astype(np.float)

    # compute edge map for reference image
    # returns 3D image. 1st dim is the edge-direction. 1st component is
    # vertical; 2nd component is hor. responses
    refSobel_sep = bob.ip.base.sobel(refImage)
    refSobelX = refSobel_sep[0, :, :]
    refSobelY = refSobel_sep[1, :, :]
    if orientation is 'horizontal':
        refEdge = iqm.edge_thinning(refSobelX[:, :], refSobelX[:, :], thinning)
    else:
        if orientation is 'vertical':
            refEdge = iqm.edge_thinning(
                refSobelY[
                    :, :], refSobelY[
                    :, :], thinning)
        else:
            refEdge = iqm.edge_thinning(
                refSobelX[
                    :, :], refSobelY[
                    :, :], thinning)

    return refEdge


def compute_msu_iqa_features(rgbImage):
    """Computes image-quality features for the given input color (RGB) image.
    This is the main function to call.

    Parameters:

    rgbImage (:py:class:`numpy.ndarray`): A ``uint8`` array with 3 dimensions,
        representing the RGB input image of shape [3,M,N] (M rows x N cols).

    Returns:

    featSet (:py:class:`numpy.ndarray`): a 1D numpy array of 121 float32
        scalars. This function returns the image-quality features (for face
        anti- spoofing) that have been described by Wen et al. in their paper:
        "Face  spoof  detection  with  image distortion analysis", IEEE Trans.
        on Information Forensics and Security, vol. 10(4), pp. 746-761, April
        2015.
    """
    rgbImage = rgbImage.copy()
    assert len(
        rgbImage.shape) == 3, 'compute_msu_iqa_features():: image should be ' \
        'a 3D array (containing a rgb image)'
    # defined above. Calls Bob's rgb_to_hsv() after rescaling the input image.
    h, s, v = matlab_rgb2hsv(rgbImage)

    grayImage = np.zeros_like(h, dtype='uint8')
    bob.ip.color.rgb_to_gray(rgbImage, grayImage)

    # compute blur-features
    blurFeat = blurriness(grayImage)

    pinaBlur = marzilianoBlur(grayImage)
    pinaBlur /= 30.0

    # compute color-diversity features
    colorHist, totNumColors = calColorHist(rgbImage)
    totNumColors /= 2000.0  # as done in Matlab code provided by MSU.

    # calculate mean, deviation and skewness of each channel
    # use histogram shifting for the hue channel
    momentFeatsH = calmoment_shift(h)

    momentFeats = momentFeatsH.copy()
    momentFeatsS = calmoment(s)
    momentFeats = np.hstack((momentFeats, momentFeatsS))
    momentFeatsV = calmoment(v)
    momentFeats = np.hstack((momentFeats, momentFeatsV))

    # compute the image-specularity features
    speckleFeats = compute_iqa_specularity_features(rgbImage, startEps=0.06)

    # stack the various feature-values in the same order as in MSU's matlab
    # code.
    fv = speckleFeats.copy()

    fv = np.hstack((fv, momentFeats))
    fv = np.hstack((fv, colorHist))
    fv = np.hstack((fv, totNumColors))
    fv = np.hstack((fv, blurFeat))
    fv = np.hstack((fv, pinaBlur))

    return fv


def compute_iqa_specularity_features(rgbImage, startEps=0.05):
    """Returns three features characterizing the specularity present in input
    color image. First the specular and diffuse components of the input image
    are separated using the
    """

    # separate the specular and diffuse components of input color image.
    # original python version
    #speckleFreeImg, diffuseImg, speckleImg = tsh.remove_highlights(
    #    rgbImage.astype(float), startEps, verboseFlag=False)

    speckleFreeImg, diffuseImg, speckleImg = remove_highlights(
            rgbImage.astype(np.float32), startEps)

    speckleImg[np.where(np.isinf(speckleImg))] = 0
    speckleImg[np.where(np.isnan(speckleImg))] = 0
    speckleImg[np.where(speckleImg < 0)] = 0
    speckleImg[np.where(speckleImg > 255)] = 255

    # speckleImg contains the specular-component

    if len(speckleImg.shape) == 3:
        speckleImg = speckleImg[0]
    speckleImg = speckleImg.clip(min=0)

    speckleMean = np.mean(speckleImg)
    # factors 1.5 and 4.0 are proposed by Wen et al. in their paper and matlab
    # code.
    lowSpeckleThresh = speckleMean * 1.5
    hiSpeckleThresh = speckleMean * 4.0
    specklePixels = speckleImg[
        np.where(
            np.logical_and(
                speckleImg >= lowSpeckleThresh,
                speckleImg < hiSpeckleThresh))]

    # percentage of specular pixels in image
    r = float(specklePixels.flatten().shape[
              0]) / (speckleImg.shape[0] * speckleImg.shape[1])
    m = np.mean(specklePixels)  # mean-specularity (of specular-pixels)
    s = np.std(specklePixels)  # std. of specularity (of specular-pixels)

    # scaling by factor of 150 is as done by Wen et al. in their matlab code.
    return np.asarray((r, m / 150.0, s / 150.0), dtype=np.float32)


def marzilianoBlur(image):
    """Method proposed by Marziliano et al. for determining the average width
    of vertical edges, as a measure of blurredness in an image. (Reimplemented
    from the Matlab code provided by MSU.)

    :param image: 2D gray-level (face) image
    :param regionMask: (optional) 2D matrix (binary image), where 1s mark the
        pixels belonging to a region of interest, and 0s indicate pixels
        outside ROI.
    """

    assert len(
        image.shape) == 2, 'marzilianoBlur():: input image should be ' \
                           'a 2D array (gray level image)'

    # compute vertical edge-map of image using sobel
    edgeMap = sobelEdgeMap(image, 'vertical')

    # There will be some difference between the result of this function and the
    # Matlab version, because the edgeMap produced by sobelEdgeMap() is not
    # exactly the same as that produced by Matlab's edge() function. Test edge-
    # map generated in Matlab produces the same result as the matlab version of
    # MarzilianoBlur().

    blurImg = image
    C = blurImg.shape[1]  # number of cols in image
    # row, col contain the indices of the pixels that comprise edge-map.
    (row, col) = edgeMap.nonzero()

    blurMetric = 0
    if len(row) > 0:

        # to make the following code work in a similar fashion to the original
        # matlab code, sort the cols in ascending order, and sort the rows
        # according to the cols.
        #     ind = np.lexsort((row,col))
        #     row = row[ind]
        #     col = col[ind]
        # print('lexsort_col: %d' % (1+col))
        # print('lexsort_row: %d' % (1+row))
        # This was only used for debugging (to compare with Matlab code). In
        # fact it is not necessary, so it is commented out.

        edgeWidths = np.zeros_like(row, dtype=int)

        for i in range(len(row)):
            rEdge = row[i]
            cEdge = col[i]
            # instead of setting them to 'inf' as in MSU's Matlab version
            cStart = 0
            cEnd = 0

            # we want to estimate the edge-width, which will be cEnd - cStart.

            # search for start of edge in horizontal direction
            if cEdge > 0:  # i.e., edge is not on the left-border
                # 2.1: search left of current pixel (backwards)
                if blurImg[
                        rEdge,
                        cEdge] > blurImg[
                        rEdge,
                        cEdge -
                        1]:  # edge corresponds to a local peak; estimate left-
                        # extent of peak
                    j = cEdge - 1
                    while j > 0 and blurImg[rEdge, j] >= blurImg[rEdge, j - 1]:
                        j -= 1
                    cStart = j
                else:  # edge corresponds to a local valley; determine left-
                    # extent of valley
                    j = cEdge - 1
                    while j > 0 and blurImg[rEdge, j] <= blurImg[rEdge, j - 1]:
                        j -= 1
                    cStart = j

            # search for end of edge in horizontal direction
            cEnd = C - 1  # initialize to right-border of image -- the max.
            # possible position for cEnd
            if cEdge < C - 1:
                if blurImg[
                        rEdge,
                        cEdge] > blurImg[
                        rEdge,
                        cEdge +
                        1]:
                    # edge corresponds to a local peak; estimate right-extent
                    # of peak
                    j = cEdge + 1
                    while j < C - 1 and blurImg[rEdge,
                                                j] >= blurImg[rEdge, j + 1]:
                        j += 1
                    cEnd = j
                else:
                    # edge corresponds to a local valley; determine right-
                    # extent of valley
                    j = cEdge + 1
                    while j < C - 1 and blurImg[rEdge,
                                                j] <= blurImg[rEdge, j + 1]:
                        j += 1
                    cEnd = j

            edgeWidths[i] = cEnd - cStart

            # sanity-check (edgeWidths should not have negative values)
            negSum = np.sum(edgeWidths[np.where(edgeWidths < 0)])
            assert negSum == 0, 'marzilianoBlur():: edgeWidths[] contains ' \
                                'negative values. YOU CANNOT BE SERIOUS!'

        # Final metric computation
        blurMetric = np.mean(edgeWidths)

    # compute histogram of edgeWidths ...(later)
        # binnum = 100;
        # t = ((1:binnum) - .5) .* C ./ binnum;
        # whist = hist(width_array, t) ./ length(width_array);

    return blurMetric

def calmoment(channel, regionMask=None):
    """ returns the first 3 statistical moments (mean, standard-dev., skewness)
    and 2 other first-order statistical measures of input image
    :param channel: 2D array containing gray-image-like data
    """

    assert len(
        channel.shape) == 2, 'calmoment():: channel should be ' \
                             'a 2D array (a single color-channel)'

    t = np.arange(0.05, 1.05, 0.05) + 0.025                 # t = 0.05:0.05:1;

    # pixnum = length(channel(:));
    nPix = np.prod(channel.shape)
    m = np.mean(channel)                            # m = mean(channel(:));
    # d = sqrt(sum((channel(:) - m) .^ 2) / pixnum);
    d = np.std(channel)
    # s = sum(((channel(:) - m) ./ d) .^ 3) / pixnum;
    s = np.sum(np.power(((channel - m) / d), 3)) / nPix
    # print(t)
    myHH = np.histogram(channel, t)[0]
    # print(myHH)
    # hh = hist(channel(:),t) / pixnum;
    hh = myHH.astype(float) / nPix

    # H = np.array([m,d,s, np.sum(hh[0:1]), np.sum(hh[-2:-1])])  # H = [m d s
    # sum(hh(1:2)) sum(hh(end-1:end))];
    H = np.array([m, d, s])
    s0 = np.sum(hh[0:2])
    # print(s0)
    H = np.hstack((H, s0))
    s1 = np.sum(hh[-2:])
    # print(s1)
    H = np.hstack((H, s1))

    return H


def calmoment_shift(channel):
    assert len(
        channel.shape) == 2, 'calmoment_shift():: channel should be a ' \
                             '2D array (a single color-channel)'

    channel = channel + 0.5
    channel[np.where(channel > 1.0)] -= 1.0

    H = calmoment(channel)

    return H


def calColorHist(image, m=100):
    """
    function returns the top 'm' most popular colors in the input image
        :param image: RGB color-image represented in a 3D array
        :param m: integer specifying how many 'top' colors to be counted (e.g.
            for m=10 the function will return the pixel-counts for the top 10
            most popular colors in image)
        :return cHist: counts of the top 100 most popular colors in image
        :return numClrs: total number of distinct colors in image
    """
    # 1. compute color histogram of image (normalized, if specified)
    numBins = 32
    maxval = 255
    cHist = rgbhist(image, maxval, numBins, 1)

    # 2. determine top 100 colors of image from histogram
    y = sorted(cHist, reverse=True)  # [Y, I] = sort(H,'descend');
    cHist = y[0:m]                    # H = Y(1:m)';

    c = np.cumsum(y)                # C = cumsum(Y);
    numClrs = np.where(c > 0.99)[0][0]    # clrnum = find(C>.99,1,'first') - 1;

    cHist = np.array(cHist)
    return cHist, numClrs


'''
computes 3d color histogram of image
'''


def rgbhist(image, maxval, nBins, normType=0):
    assert len(image.shape) == 3, 'image should be a 3D (rgb) array of shape' \
        ' (3, m,n) where m is no. of rows, and n is no. if cols in image.c$'
    assert normType > -1 and normType < 2, 'rgbhist():: normType should ' \
        ' be only 0 or 1'
    # zeros([nBins nBins nBins]);
    H = np.zeros((nBins, nBins, nBins), dtype=np.uint32)

    decimator = (maxval + 1) / nBins
    numPix = image.shape[1] * image.shape[2]
    # im = reshape(I,[size(I,1)*size(I,2) 3]);
    im = image.reshape(3, numPix).copy()
    im = im.T

    p = np.floor(im.astype(float) / decimator).astype(np.uint32)
    # in future versions of numpy (1.13 and above) you can replace this with:
    # unique_p, count = np.unique(p, return_counts=True, axis=0)
    # the following lines were taken from: https://stackoverflow.com/a/16973510
    p2 = np.ascontiguousarray(p).view(
        np.dtype((np.void, p.dtype.itemsize * p.shape[1])))
    unique_p, count = np.unique(p2, return_counts=True)
    unique_p = unique_p.view(p.dtype).reshape(-1, p.shape[1])
    # till here
    H[unique_p[:, 0], unique_p[:, 1], unique_p[:, 2]] = count

    H = H.ravel()  # H = H(:);
    # Un-Normalized histogram

    if normType == 1:
        H = H.astype(np.float32) / np.sum(H)    # l1 normalization
    return H


def blurriness(image):
    """
    function to estimate blurriness of an image, as computed by Di Wen et al.
    in their IEEE-TIFS-2015 paper.
        :param image: a gray-level image
    """

    assert len(
        image.shape) == 2, 'Input to blurriness() function should ' \
                           'be a 2D (gray) image'

    d = 4
    fsize = 2 * d + 1
    kver = np.ones((1, fsize)) / fsize
    khor = kver.T

    Bver = ssg.convolve2d(
        image.astype(
            np.float32), kver.astype(
            np.float32), mode='same')
    Bhor = ssg.convolve2d(
        image.astype(
            np.float32), khor.astype(
            np.float32), mode='same')

    # implementations of DFver and DFhor below don't look the same as in the
    # Matlab code, but the following implementation produces equivalent
    # results. there might be a bug in Matlab! The 2 commented statements above
    # would correspond to the intent of the Matlab code.
    DFver = np.diff(image.astype('int16'), axis=0)
    DFver[np.where(DFver < 0)] = 0

    DFhor = np.diff(image.astype('int16'), axis=1)
    DFhor[np.where(DFhor < 0)] = 0

    DBver = np.abs(np.diff(Bver, axis=0))
    DBhor = np.abs(np.diff(Bhor, axis=1))

    Vver = DFver.astype(float) - DBver.astype(float)
    Vhor = DFhor.astype(float) - DBhor.astype(float)
    Vver[Vver < 0] = 0  # Vver(find(Vver<0)) = 0;
    Vhor[Vhor < 0] = 0  # Vhor(find(Vhor<0)) = 0;

    SFver = np.sum(DFver)
    SFhor = np.sum(DFhor)  # sum(DFhor(:));

    SVver = np.sum(Vver)  # sum(Vver(:));
    SVhor = np.sum(Vhor)  # sum(Vhor(:));

    BFver = (SFver - SVver) / SFver
    BFhor = (SFhor - SVhor) / SFhor

    blurF = max(BFver, BFhor)  # max([BFver BFhor]);

    return blurF
