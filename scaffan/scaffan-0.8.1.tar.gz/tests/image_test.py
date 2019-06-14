#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest
import os.path as op
from nose.plugins.attrib import attr

path_to_script = op.dirname(op.abspath(__file__))

import sys

sys.path.insert(0, op.abspath(op.join(path_to_script, "../../io3d")))
sys.path.insert(0, op.abspath(op.join(path_to_script, "../../imma")))
# import sys
# import os.path

# imcut_path =  os.path.join(path_to_script, "../../imcut/")
# sys.path.insert(0, imcut_path)

import glob
import os
import numpy as np
import matplotlib.pyplot as plt

skip_on_local = False

import scaffan.image as scim
scim.import_openslide()
import openslide

import io3d
import scaffan
import scaffan.image as scim


class ParseAnnotationTest(unittest.TestCase):

    def test_get_pixelsize_on_different_levels(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        logger.debug("filename {}".format(fn))
        imsl = openslide.OpenSlide(fn)

        pixelsize1, pixelunit1 = scim.get_pixelsize(imsl)
        self.assertGreater(pixelsize1[0], 0)
        self.assertGreater(pixelsize1[1], 0)

        pixelsize2, pixelunit2 = scim.get_pixelsize(imsl, level=2)
        self.assertGreater(pixelsize2[0], 0)
        self.assertGreater(pixelsize2[1], 0)

        self.assertGreater(pixelsize2[0], pixelsize1[0])
        self.assertGreater(pixelsize2[1], pixelsize1[1])

    def test_anim(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        offset = anim.get_offset_px()
        self.assertEqual(len(offset), 2, "should be 2D")
        im = anim.get_image_by_center((10000, 10000), as_gray=True )
        self.assertEqual(len(im.shape), 2, "should be 2D")

        annotations = anim.read_annotations()
        self.assertGreater(len(annotations), 1, "there should be 2 annotations")

    def test_file_info(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        msg = anim.get_file_info()
        self.assertEqual(type(msg), str)
        self.assertLess(0, msg.find("mm"))

    def test_region(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        anim.set_region_on_annotations(0, 3)
        mask = anim.get_annotation_region_raster(0)
        image = anim.get_region_image()
        plt.imshow(image)
        plt.contour(mask)
        # plt.show()
        self.assertGreater(np.sum(mask), 20)

    def test_region_select_by_title(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        anim.set_region_on_annotations("obj1", 3)
        mask = anim.get_annotation_region_raster("obj1")
        image = anim.get_region_image()
        plt.imshow(image)
        plt.contour(mask)
        # plt.show()
        self.assertGreater(np.sum(mask), 20)
        self.assertTrue(np.array_equal(mask.shape[:2], image.shape[:2]), "shape of mask should be the same as shape of image")

    def test_select_view_by_title_and_plot(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        annotation_ids = anim.select_annotations_by_title("obj1")
        view = anim.get_views(annotation_ids)[0]
        image = view.get_region_image()
        plt.imshow(image)
        view.plot_annotations("obj1")
        # plt.show()
        self.assertGreater(image.shape[0], 100)
        mask = view.get_annotation_region_raster("obj1")
        self.assertTrue(np.array_equal(mask.shape[:2], image.shape[:2]), "shape of mask should be the same as shape of image")

    def test_select_view_by_title_and_plot_floating_resolution(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        annotation_ids = anim.select_annotations_by_title("obj1")
        view = anim.get_views(annotation_ids)[0]
        pxsize, pxunit = view.get_pixelsize_on_level()
        image = view.get_region_image()
        plt.subplot(221)
        plt.imshow(image)
        view.plot_annotations("obj1")
        plt.suptitle("{} x {} [{}]".format(pxsize[0], pxsize[1], pxunit))

        self.assertGreater(image.shape[0], 100)
        mask = view.get_annotation_region_raster("obj1")
        self.assertTrue(np.array_equal(mask.shape[:2], image.shape[:2]), "shape of mask should be the same as shape of image")
        plt.subplot(222)
        plt.imshow(mask)



        view2 = view.to_pixelsize(pixelsize_mm=[0.01, 0.01])
        image2 = view2.get_region_image()
        plt.subplot(223)
        plt.imshow(image2)
        view2.plot_annotations("obj1")
        mask = view2.get_annotation_region_raster("obj1")
        plt.subplot(224)
        plt.imshow(mask)
        self.assertTrue(np.array_equal(mask.shape[:2], image2.shape[:2]), "shape of mask should be the same as shape of image")

        # plt.show()

    def test_merge_views(self):
        """
        Create two views with based on same annotation with different margin. Resize the inner to low resolution.
        Insert the inner image with low resolution into big image on high resolution.
        :return:
        """
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        annotation_ids = anim.select_annotations_by_title("obj1")
        view1 = anim.get_views(annotation_ids, margin=1.0, pixelsize_mm=[0.005, 0.005])[0]
        image1 = view1.get_region_image()
        import copy
        image1_copy = copy.copy(image1)
        # plt.imshow(image1)
        # plt.show()

        view2 = anim.get_views(annotation_ids, margin=0.1, pixelsize_mm=[0.05, 0.05])[0]
        image2 = view2.get_region_image()
        # plt.imshow(image2)
        # plt.show()

        merged = view1.insert_image_from_view(view2, image1, image2)

        plt.imshow(merged)
        errim = np.mean(np.abs(image1_copy.astype(np.int) - merged), 2)
        # plt.figure()
        # plt.imshow(errim)
        # plt.show()
        err = np.mean(errim)
        self.assertLess(err, 3, "Mean error in intensity levels per pixel should be low")
        self.assertLess(1, err, "Mean error in intensity levels per pixel should be low but there should be some error.")


    def test_view_margin_size(self):
        """
        Compare two same resolution images with different margin
        :return:
        """
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = scim.AnnotatedImage(fn)
        annotation_ids = anim.select_annotations_by_title("obj1")

        img1 = anim.get_views(annotation_ids, margin=0.0, pixelsize_mm=[0.005, 0.005])[0].get_region_image(as_gray=True)
        img2 = anim.get_views(annotation_ids, margin=1.0, pixelsize_mm=[0.005, 0.005])[0].get_region_image(as_gray=True)

        sh1 = np.asarray(img1.shape)
        sh2 = np.asarray(img2.shape)
        self.assertTrue(np.all((sh1 * 2.9 ) < sh2), "Boundary adds 2*margin*size of image to the image size")
        self.assertTrue(np.all(sh2 < (sh1 * 3.1 )), "Boundary adds 2*margin*size of image to the image size")


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr)
    logger.setLevel(logging.DEBUG)
    unittest.main()
