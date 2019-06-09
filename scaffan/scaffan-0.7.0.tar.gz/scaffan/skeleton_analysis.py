# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process lobulus analysis.
"""

from loguru import logger
import skimage.filters
from skimage.morphology import skeletonize
import skimage.io
import scipy.signal
import scipy.ndimage
import os.path as op
import numpy as np
import warnings
import morphsnakes as ms
from matplotlib import pyplot as plt
from scaffan import image as scim
import scaffan
import scaffan.lobulus
from .report import Report
from pyqtgraph.parametertree import Parameter
import imma.image


class SkeletonAnalysis:
    def __init__(self):

        params = [
            # {
            #     "name": "Tile Size",
            #     "type": "int",
            #     "value" : 128
            # },
            {
                "name": "Working Resolution",
                "type": "float",
                # "value": 0.000001,
                "value": 0.00000091, # this is typical resolution on level 2
                # "value": 0.00000182,  # this is typical resolution on level 3
                # "value": 0.00000364,  # this is typical resolution on level 4
                # "value": 0.00000728,  # this is typical resolution on level 5
                # "value": 0.00001456,  # this is typical resolution on level 6
                "suffix": "m",
                "siPrefix": True

            },
            {
                "name": "Inner Lobulus Margin",
                "type": "float",
                "value": 0.00002,
                "suffix": "m",
                "siPrefix": True,
                "tip": "Area close to the border is ignored in Otsu threshold computation before skeletonization step."
            },

        ]

        self.parameters = Parameter.create(name="Skeleton Analysis", type="group", children=params, expanded=False)
        self.report: Report = None

    def set_report(self, report: Report):
        self.report = report

    def set_lobulus(self, lobulus: scaffan.lobulus.Lobulus):
        self.lobulus: scaffan.lobulus.Lobulus = lobulus
        pixelsize_mm = [(self.parameters.param("Working Resolution").value() * 1000)] * 2
        self.view = self.lobulus.view.to_pixelsize(pixelsize_mm=pixelsize_mm)

    def skeleton_analysis(self, show=False):
        datarow = {}

        inner = self.lobulus.central_vein_mask
        # TODO Split the function here
        inner_lobulus_margin_mm = self.parameters.param("Inner Lobulus Margin").value() * 1000

        # eroded image for threshold analysis
        dstmask = scipy.ndimage.morphology.distance_transform_edt(
            self.lobulus.lobulus_mask, self.lobulus.view.region_pixelsize[::-1]
        )
        inner_lobulus_mask = dstmask > inner_lobulus_margin_mm
        # print("inner_lobulus_mask" , np.sum(inner_lobulus_mask==0), np.sum(inner_lobulus_mask==1))

        # detail_level = 2
        new_size = self.view.get_size_on_pixelsize_mm()

        resize_params = dict(
            output_shape=[new_size[1], new_size[0]],
            mode="reflect",
            order=0,
            anti_aliasing=False,
        )
        detail_mask = skimage.transform.resize(self.lobulus.lobulus_mask, **resize_params)
        detail_inner_lobulus_mask = skimage.transform.resize(
            inner_lobulus_mask, **resize_params
        )
        detail_central_vein_mask = skimage.transform.resize(inner == 1, **resize_params)

        detail_view = self.view
        detail_image = detail_view.get_region_image(as_gray=True)
        fig = plt.figure()
        plt.imshow(detail_image)
        plt.contour(detail_mask + detail_inner_lobulus_mask)
        detail_view.add_ticks()
        if self.report is not None:
            self.report.savefig_and_show(
                "skeleton_analysis_detail_image_and_mask_{}.png".format(self.lobulus.annotation_id),
                fig,
            )

        threshold = skimage.filters.threshold_otsu(
            detail_image[detail_inner_lobulus_mask == 1]
        )
        imthr = detail_image < threshold
        imthr[detail_mask != 1] = 0
        # plt.figure()
        # plt.imshow(imthr)
        # if show:
        #     plt.show()
        skeleton = skeletonize(imthr)
        datarow["Skeleton length"] = np.sum(skeleton) * detail_view.region_pixelsize[0]
        datarow["Output pixel size 0"] = detail_view.region_pixelsize[0]
        datarow["Output pixel size 1"] = detail_view.region_pixelsize[1]
        datarow["Output image size 0"] = (
                detail_view.region_pixelsize[0] * imthr.shape[0]
        )
        datarow["Output image size 1"] = (
                detail_view.region_pixelsize[1] * imthr.shape[1]
        )
        fig = plt.figure(figsize=(12, 10))
        plt.imshow(skeleton + imthr)
        detail_view.add_ticks()
        if self.report is not None:
            self.report.savefig_and_show(
                "thumb_skeleton_thr_{}.png".format(self.lobulus.annotation_id), fig
            )

        if self.report is not None:
            imall = detail_mask.astype(np.uint8)
            imall[detail_central_vein_mask > 0] = 2
            imall[imthr > 0] = 3
            imall[skeleton > 0] = 4
            # imall = (skeleton.astype(np.uint8) + imthr.astype(np.uint8) +  + (detail_central_vein_mask.astype(np.uint8) * 2)).astype(np.uint8)
            self.imsave("lobulus_central_thr_skeleton_{}.png", imall)
            self.imsave(
                "lobulus_thr_skeleton_{}.png",
                (skeleton.astype(np.uint8) + imthr + detail_mask).astype(np.uint8),
            )
            self.imsave("skeleton_{}.png", skeleton)
            self.imsave("thr_{}.png", imthr)
            # plt.imsave(op.join(self.report.outputdir, "skeleton_thr_lobulus_{}.png".format(self.annotation_id)), skeleton.astype(np.uint8) + imthr + detail_mask)
            # plt.imsave(op.join(self.report.outputdir, "skeleton_{}.png".format(self.annotation_id)), skeleton)
            # plt.imsave(op.join(self.report.outputdir, "thr_{}.png".format(self.annotation_id)), imthr)
            # skimage.io.imsave(op.join(self.report.outputdir, "raw_skeleton_thr_lobulus_{}.png".format(self.annotation_id)),
            #                   (50 * skeleton + 50 * imthr + 50 * detail_mask).astype(np.uint8))
            # skimage.io.imsave(op.join(self.report.outputdir, "raw_skeleton_{}.png".format(self.annotation_id)), 50 * skeleton)
            # skimage.io.imsave(op.join(self.report.outputdir, "raw_thr_{}.png".format(self.annotation_id)), 50 * imthr)

        conv = scipy.signal.convolve2d(skeleton, np.ones([3, 3]), mode="same")
        conv = conv * skeleton
        fig = plt.figure(figsize=(12, 10))
        plt.imshow(conv)
        detail_view.add_ticks()
        if self.report is not None:
            self.report.savefig_and_show(
                "figure_skeleton_nodes_{}.png".format(self.lobulus.annotation_id),
                fig
            )

            with warnings.catch_warnings():
                # warnings.simplefilter("low contrast image")
                warnings.filterwarnings("ignore", ".*low contrast image.*")
                self.imsave("skeleton_nodes_{}.png", imthr, 20)
            # plt.imsave(op.join(self.report.outputdir, "skeleton_nodes_{}.png".format(self.annotation_id)), conv.astype(np.uint8))
            # skimage.io.imsave(op.join(self.report.outputdir, "raw_skeleton_nodes_{}.png".format(self.annotation_id)), (conv * 20).astype(np.uint8))

        conv[conv > 3] = 0
        label, num = scipy.ndimage.label(conv)
        datarow["Branch number"] = num
        label, num = scipy.ndimage.label(conv == 1)
        datarow["Dead ends number"] = num

        self.report.add_cols_to_actual_row(datarow)

    def imsave(self, base_fn, arr, k=50):
        base_fn = base_fn.format(self.lobulus.annotation_id)
        self.report.imsave(base_fn, arr, k)
