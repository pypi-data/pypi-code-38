# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process lobulus analysis.
"""

from loguru import logger
import skimage.filters
from skimage.morphology import skeletonize
import skimage.io
import copy
import scipy.signal
import scipy.ndimage
import os.path as op
import numpy as np
import warnings
import morphsnakes as ms
from matplotlib import pyplot as plt
from scaffan import image as scim
from .report import Report
from pyqtgraph.parametertree import Parameter
import imma.image
import scaffan.texture

_cite = "" +\
    "[1]: A Morphological Approach to Curvature-based Evolution of Curves and Surfaces, Pablo Márquez-Neila, Luis Baumela and Luis Álvarez. In IEEE Transactions on Pattern Analysis and Machine Intelligence (PAMI), 2014, DOI 10.1109/TPAMI.2013.106" +\
    "[2]: Morphological Snakes. Luis Álvarez, Luis Baumela, Pablo Márquez-Neila. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition 2010 (CVPR10)."

class Lobulus:
    def __init__(self):
        # TODO the segmentation resolution was probably different.
        #  For segmentation was used different level than 2. Probably 3 or 4
        #  The level 2 has been used in detail view

        self._inner_texture = scaffan.texture.GLCMTextureMeasurement("central_vein")
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
                # "value": 0.000001,  # this is typical resolution on level 2-3
                # "value": 0.000002,  # this is typical resolution on level 3-4
                # "value": 0.0000015,  # this is typical resolution on level 3-4
                # "value": 0.000000227 # level 0
                # "value": 0.000000454 # level 1
                # "value": 0.000000908 # level 2
                # "value": 0.00000091, # this is typical resolution on level 2
                "value": 0.00000182,  # this is typical resolution on level 3 # probably prev stable version
                # "value": 0.00000364,  # this is typical resolution on level 4
                # "value": 0.00000728,  # this is typical resolution on level 5
                # "value": 0.00001456,  # this is typical resolution on level 6
                "suffix": "m",
                "siPrefix": True

            },
            {
                "name": "Annotation Margin",
                "type": "float",
                "value": 180,
                "suffix": "%",
                "siPrefix": False,
                "tip": "Margin added to the input annotation where is expected whole lobulus."
            },
            {
                'name': 'Border Segmentation', 'type': 'group',
                'tip': "MorphACWE algorithm parameters. " + _cite,
                'children': [
                    {
                        "name": "Smoothing",
                        "type": "float",
                        "value": 2,
                        "suffix": "px",
                        "siPrefix": False,
                        "tip": "MorphACWE algorithm parameter: The number of repetitions of the smoothing step (the curv operator) in each iteration. In other terms, this is the strength of the smoothing. This is the parameter µ."
                    },
                    {
                        "name": "Lambda1",
                        "type": "float",
                        "value": 1.,
                        'tip': "MorphACWE algorithm parameter: Relative importance of the inside pixels (lambda1) against the outside pixels (lambda2).",
                        # "suffix": "px",
                        # "siPrefix": False
                    },
                    {
                        "name": "Lambda2",
                        "type": "float",
                        "value": 2.,
                        'tip': "MorphACWE algorithm parameter: Relative importance of the inside pixels (lambda1) against the outside pixels (lambda2).",
                        # "suffix": "px",
                        # "siPrefix": False
                    },
                    {
                        "name": "Iterations",
                        "type": "int",
                        # "value": 180
                        "value": 400
                    },


                ]
            },
            {
                'name': 'Central Vein Segmentation', 'type': 'group',
                'tip': "MorphGAC algorithm parameters. " + _cite,
                'children': [
                {
                    "name": "Smoothing",
                    "type": "float",
                    "value": 2,
                    "suffix": "px",
                    "siPrefix": False,
                    "tip": "MorphGAC algorithm parameter: The number of repetitions of the smoothing step in each iteration. This is the parameter µ."
                },
                {

                    "name": "Threshold",
                    "type": "float",
                    # "value": 0.28, # prev stable version
                    # "value": 0.35,
                    # "value": 0.25,
                    "value": 0.22,
                    # "value": 0.25,
                    'tip': "MorphGAC algorithm parameter: The threshold that determines which areas are affected by the morphological balloon. This is the parameter θ.",
                    # "suffix": "px",
                    # "siPrefix": False
                },
                {
                    "name": "Ballon",
                    "type": "float",
                    "value": -1,
                    'tip': "MorphGAC algorithm parameter: The strength of the morphological balloon. This is the parameter ν.",
                    # "suffix": "px",
                    # "siPrefix": False
                },
                {
                    "name": "Iterations",
                    "type": "int",
                    # "value": 400
                    "value": 150
                },
                self._inner_texture.parameters,


            ]
            },

        ]

        self.parameters = Parameter.create(name="Lobulus Segmentation", type="group", children=params, expanded=False)
        self.report: Report = None

    def set_annotated_image_and_id(self, anim: scim.AnnotatedImage, annotation_id, level=None):
        """

        :param anim:
        :param annotation_id:
        :param level: Is used just for short time in funcion get_views()
        :return:
        """
        self.anim = anim
        self.level = level
        self.annotation_id = annotation_id
        self._init_by_annotation_id(annotation_id)

        pass

    def set_report(self, report: Report):
        self.report: Report = report

    def _init_by_annotation_id(self, annotation_id):
        if not np.isscalar(annotation_id):
            raise ValueError("Annotation ID should be scalar int value for lobulus processing.")

        pixelsize_mm = [(self.parameters.param("Working Resolution").value() * 1000)] * 2
        annotation_margin = (self.parameters.param("Annotation Margin").value() * 0.01)
        self.view = self.anim.get_views(
            annotation_ids=[annotation_id], level=self.level, margin=annotation_margin,
            pixelsize_mm=pixelsize_mm
        )[0]
        # right_shape = imma.image.calculate_new_shape(
        #     self.view.region_size_on_level,
        #     self.view.get_pixelsize_on_level(self.view.region_level)[0],
        #     self.view.region_pixelsize
        # )
        self.image = self.view.get_region_image(as_gray=True)
        self.annotation_mask = self.view.get_annotation_region_raster(annotation_id=annotation_id)
        # self.anim.titles
        # self.anim.details
        pass


    def find_border(self, show=True):
        self._im_gradient_border_frangi = skimage.filters.frangi(self.image)
        logger.debug("Image size {}".format(self.image.shape))
        circle = self.annotation_mask
        if self.report is not None:
            self.report.imsave_as_fig("gradient_outer.png", self._im_gradient_border_frangi)
        param_acwe_smoothing = self.parameters.param("Border Segmentation", "Smoothing").value()
        param_acwe_lambda1 =   self.parameters.param("Border Segmentation", "Lambda1").value()
        param_acwe_lambda2 =   self.parameters.param("Border Segmentation", "Lambda2").value()
        param_acwe_iterations =self.parameters.param("Border Segmentation", "Iterations").value()
        mgac = ms.MorphACWE(
            self._im_gradient_border_frangi,
            smoothing=param_acwe_smoothing,
            lambda1=param_acwe_lambda1,
            lambda2=param_acwe_lambda2)
        mgac.levelset = circle.copy()
        mgac.run(iterations=param_acwe_iterations)
        outer = mgac.levelset.copy()
        self.border_mask = outer

    def find_central_vein(self, show=True):
        use_texture_features = True
        pixelsize_mm = [(self.parameters.param("Working Resolution").value() * 1000)] * 2
        central_vein_view = self.view.anim.get_views([self.annotation_id], pixelsize_mm=pixelsize_mm, margin=0.1)[0]

        self._inner_texture.set_input_data(view=central_vein_view, id=self.annotation_id, lobulus_segmentation=None)
        self._inner_texture.set_report(self.report)
        self._inner_texture.add_cols_to_report = False
        self._inner_texture.run()
        tfeatures = copy.copy(self._inner_texture.measured_reatures)
        tfeatures[:, :, 2] = 1 - tfeatures[:, :, 2]
        tfeatures0 = np.mean(tfeatures, 2)
        if self.report is not None:
            self.report.imsave_as_fig("gradient_texture_color_{}.png".format(self.annotation_id), tfeatures)
            self.report.imsave_as_fig("gradient_texture_mean_{}.png".format(self.annotation_id), tfeatures0)

        sl = self.view.get_slices_for_insert_image_from_view(central_vein_view)

        image = central_vein_view.get_region_image(as_gray=True)
        im_gradient_border_frangi = self._im_gradient_border_frangi[sl]  # skimage.filters.frangi(image)
        im_gradient_base_inner = ms.gborders(image, alpha=1000, sigma=2)
        im_gradient_inner = im_gradient_base_inner - (im_gradient_border_frangi * 10000)
        if use_texture_features:
            im_gradient_inner *= (1 - imma.image.resize_to_shape(tfeatures0, im_gradient_inner.shape))
        if self.report is not None:
            self.report.imsave_as_fig("gradient_inner_frangi_{}.png".format(self.annotation_id), im_gradient_border_frangi)
            self.report.imsave_as_fig("gradient_base_inner_{}.png".format(self.annotation_id), im_gradient_base_inner)
            self.report.imsave_as_fig("gradient_inner_{}.png".format(self.annotation_id), im_gradient_inner)
        # circle = circle_level_set(imgr.shape, size2, 75, scalerow=0.75)
        circle = self.annotation_mask[sl]
        # plt.figure()
        # plt.imshow(im_gradient0)
        # plt.colorbar()
        # plt.contour(circle)
        # plt.show()
        # mgac = ms.MorphGAC(im_gradient, smoothing=2, threshold=0.3, balloon=-1)
        # mgac.levelset = circle.copy()
        # mgac.run(iterations=100)
        # inner = mgac.levelset.copy()

        param_gac_smoothing = self.parameters.param("Central Vein Segmentation", "Smoothing").value()
        param_gac_threshold = self.parameters.param("Central Vein Segmentation", "Threshold").value()
        param_gac_baloon = self.parameters.param("Central Vein Segmentation", "Ballon").value()
        param_gac_iterations = self.parameters.param("Central Vein Segmentation", "Iterations").value()

        # central vein
        mgac = ms.MorphGAC(im_gradient_inner, smoothing=param_gac_smoothing,
                           threshold=param_gac_threshold, balloon=param_gac_baloon)
        # mgac = ms.MorphGAC(im_gradient, smoothing=2, threshold=0.28, balloon=-1.0)
        # mgac = ms.MorphACWE(im_gradient0, smoothing=2, lambda1=.1, lambda2=.05)
        mgac.levelset = circle.copy()
        mgac.run(iterations=param_gac_iterations)
        inner = mgac.levelset.copy()


        if self.report is not None:
            fig = plt.figure(figsize=(12, 10))
            plt.imshow(im_gradient_inner)
            plt.colorbar()
            plt.contour(circle + inner)
            self.report.savefig_and_show("lobulus_gradient_inner_{}.png".format(self.annotation_id), fig)

        cvmask = np.zeros_like(self.border_mask)
        cvmask = self.view.insert_image_from_view(central_vein_view, cvmask, inner)
        # cvmask[sl] = inner
        self.central_vein_mask = cvmask

    def run(self, show=True):
        self.find_border(show)
        self.find_central_vein(show)
        # inner_lobulus_margin_mm = 0.02

        # mgac = ms.MorphGAC(im_gradient, smoothing=2, threshold=0.2, balloon=+1)
        # mgac = ms.MorphACWE(im_gradient0, smoothing=2, lambda1=0.5, lambda2=1.0)

        # circle = circle_level_set(imgr.shape, (200, 200), 75, scalerow=0.75)

        # plt.figure()
        # plt.imshow(im_gradient)
        # plt.colorbar()
        # plt.contour(circle + inner + outer)
        fig = plt.figure(figsize=(12, 10))
        plt.imshow(self.image, cmap="gray")
        plt.colorbar()
        plt.contour(self.annotation_mask + self.central_vein_mask + self.border_mask)
        self.view.add_ticks()

        datarow = {}
        datarow["Annotation ID"] = self.annotation_id
        numeric_id = self.anim.get_annotation_id(self.annotation_id)
        # TODO delete debug prints
        print("self.annotations_id: ", type(self.annotation_id), self.annotation_id)
        print("numeric_id: ", type(numeric_id), numeric_id)
        print("self.anim.annotations: ", type(self.anim.annotations), self.anim.annotations)

        # self.anim.annotations.
        datarow["Annotation Title"] = self.anim.annotations[numeric_id]["title"] #[self.annotation_id]
        datarow["Annotation Details"] = self.anim.annotations[numeric_id]["details"] #[self.annotation_id]
        # datarow["Annotation Details"] = self.anim.details[self.annotation_id]
        if self.report is not None:
            self.report.savefig_and_show("lobulus_{}.png".format(self.annotation_id), fig)
        self.lobulus_mask = (self.central_vein_mask + self.border_mask) == 1
        datarow["Area"] = np.sum(self.lobulus_mask) * np.prod(
            self.view.region_pixelsize
        )

        datarow["Central vein area"] = np.sum(self.central_vein_mask > 0) * np.prod(
            self.view.region_pixelsize
        )
        datarow["Area unit"] = self.view.region_pixelunit
        self.report.add_cols_to_actual_row(datarow)
        # self.skeleton_analysis(show=show)

    def imsave(self, base_fn, arr, k=50):
        base_fn = base_fn.format(self.annotation_id)
        self.report.imsave(base_fn, arr, k)

