#! /usr/bin/python
# -*- coding: utf-8 -*-

# import logging
# logger = logging.getLogger(__name__)
from loguru import logger
import unittest
import os
import os.path as op

# from nose.plugins.attrib import attr

path_to_script = op.dirname(op.abspath(__file__))

import sys
import numpy as np

sys.path.insert(0, op.abspath(op.join(path_to_script, "../../io3d")))
sys.path.insert(0, op.abspath(op.join(path_to_script, "../../imma")))
# import sys
# import os.path

# imcut_path =  os.path.join(path_to_script, "../../imcut/")
# sys.path.insert(0, imcut_path)

import matplotlib.pyplot as plt

skip_on_local = False

import scaffan.image as saim
import scaffan.texture as satex
import scaffan.texture_lbp as salbp

saim.import_openslide()
import io3d


# from scaffan.texture_lbp import local_binary_pattern


class TextureTest(unittest.TestCase):
    def test_select_view_by_title_and_plot_patch_centers(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = saim.AnnotatedImage(fn)
        annotation_ids = anim.select_annotations_by_title("obj1")
        view = anim.get_views(annotation_ids, level=3)[0]
        image = view.get_region_image()
        plt.imshow(image)
        view.plot_annotations("obj1")
        # plt.show()
        self.assertGreater(image.shape[0], 100)
        mask = view.get_annotation_region_raster("obj1")
        self.assertTrue(
            np.array_equal(mask.shape[:2], image.shape[:2]),
            "shape of mask should be the same as shape of image",
        )

        x_nz, y_nz = satex.select_texture_patch_centers_from_one_annotation(
            anim, "obj1", tile_size=32, level=3, step=20
        )
        nz_view_px = view.coords_glob_px_to_view_px(x_nz, y_nz)
        plt.plot(nz_view_px[0], nz_view_px[1], "bo")
        # plt.show()
        # plt.gcf().clear()

        # TODO findout why are the axis swapped
        x = nz_view_px[1].astype(int)
        y = nz_view_px[0].astype(int)
        pixels = mask[(x, y)]
        self.assertTrue(
            np.all(pixels > 0), "centers positions should be inside of mask"
        )

    def test_plot(self):

        # import pdb; pdb.set_trace()
        print("test plot ...")
        plt.figure()
        print("test plot ok")

    # @unittest.skipIf(
    #     os.environ.get("TRAVIS", False), "Skip on Travis-CI #TODO make it run"
    # )
    def test_simple_texture_segmentation(self):
        # import pdb; pdb.set_trace()
        level = 0
        title_size = 128
        size = [128, 128]
        # clear all figures from prev tests
        # plt.close("all")
        # plt.gcf().clear()
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = saim.AnnotatedImage(fn)
        # import pdb; pdb.set_trace()
        ann_params = dict(tile_size=title_size, level=level, step=64)
        patch_centers0 = satex.select_texture_patch_centers_from_one_annotation(
            anim, "obj_empty", **ann_params
        )
        # import pdb; pdb.set_trace()
        patch_centers1 = satex.select_texture_patch_centers_from_one_annotation(
            anim, "obj1", **ann_params
        )
        patch_centers2 = satex.select_texture_patch_centers_from_one_annotation(
            anim, "obj2", **ann_params
        )
        patch_centers3 = satex.select_texture_patch_centers_from_one_annotation(
            anim, "obj3", **ann_params
        )
        # import pdb; pdb.set_trace()
        view0 = anim.get_view(
            center=[patch_centers0[0][0], patch_centers0[1][0]], level=level, size_on_level=size
        )
        view1 = anim.get_view(
            center=[patch_centers1[0][0], patch_centers1[1][0]], level=level, size_on_level=size
        )
        view2 = anim.get_view(
            center=[patch_centers2[0][0], patch_centers2[1][0]], level=level, size_on_level=size
        )
        view3 = anim.get_view(
            center=[patch_centers3[0][0], patch_centers3[1][0]], level=level, size_on_level=size
        )

        print("before imshow 1")
        # import pdb; pdb.set_trace()
        imrgb = view1.get_region_image(as_gray=False)
        # import pdb; pdb.set_trace()
        plt.imshow(imrgb)
        print("before first figure")
        # import pdb; pdb.set_trace()
        # plt.show()
        plt.figure()
        print("before imshow 2")
        plt.imshow(view2.get_region_image(as_gray=False))
        plt.figure()
        print("before imshow 3")
        plt.imshow(view3.get_region_image(as_gray=False))
        # plt.show()
        print("before get image")
        im0 = view0.get_region_image(as_gray=True)
        im1 = view1.get_region_image(as_gray=True)
        im2 = view2.get_region_image(as_gray=True)
        im3 = view3.get_region_image(as_gray=True)
        radius = 3
        n_points = 8
        METHOD = "uniform"
        # refs = {
        #     0: local_binary_pattern(im0, n_points, radius, METHOD),
        #     1: local_binary_pattern(im1, n_points, radius, METHOD),
        #     2: local_binary_pattern(im2, n_points, radius, METHOD),
        #     3: local_binary_pattern(im3, n_points, radius, METHOD)
        # }
        print("before lbp")
        refs = [
            [0, salbp.lbp_fv(im0)],  # n_points, radius, METHOD)],
            [1, salbp.lbp_fv(im1)],  # n_points, radius, METHOD)],
            [2, salbp.lbp_fv(im2)],  # n_points, radius, METHOD)],
            [3, salbp.lbp_fv(im3)],  # n_points, radius, METHOD)]
        ]
        print("before annotation")
        annotation_ids = anim.select_annotations_by_title("test2")
        view_test = anim.get_views(annotation_ids, level=level)[0]
        test_image = view_test.get_region_image(as_gray=True)
        target, data = list(zip(*refs))
        print("before fit")
        cls = salbp.KLDClassifier()
        cls.fit(data, target)
        tile_fnc = lambda tile: satex.get_feature_and_predict(tile, salbp.lbp_fv, cls)
        print("before tile processing")
        seg = satex.tiles_processing(test_image, tile_fnc, tile_spacing=size)
        plt.figure()
        plt.imshow(test_image)
        plt.contour(seg)
        import skimage.color

        plt.figure()
        plt.imshow(skimage.color.label2rgb(seg, test_image))
        # plt.show()
        # plt.gcf().clear()

    def test_texture_segmentation_object(self):

        level = 0
        tile_size1 = 128
        tile_size = [128, 128]
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        anim = saim.AnnotatedImage(fn)

        texseg = satex.TextureSegmentation()
        texseg.level = level
        texseg.tile_size = tile_size
        texseg.tile_size1 = tile_size1
        texseg.step = 128

        plt.figure()
        texseg.add_training_data(anim, "obj1", 1, show=True)
        texseg.show_tiles(anim, "obj1", [0, 1, -2, -1])
        plt.figure()
        texseg.add_training_data(anim, "obj2", 2, show=True)
        plt.figure()
        texseg.add_training_data(anim, "obj3", 3, show=True)
        # plt.show()
        views = anim.get_views_by_title("test2", level=texseg.level)
        texseg.fit()
        texseg.predict(views[0], show=True)
        # plt.show()

    skip_on_local = True

    @unittest.skipIf(os.environ.get("TRAVIS", False), "Skip on Travis-CI")
    def test_texture_segmentation_object_lobulus_data(self):
        fn = io3d.datasets.join_path(
            "scaffold",
            "Hamamatsu",
            "PIG-008_P008 LL-P_HE_parenchyme perif..ndpi",
            get_root=True,
        )
        anim = saim.AnnotatedImage(fn)

        texseg = satex.TextureSegmentation()
        texseg.add_training_data(anim, "empty1", 0)
        plt.figure()
        texseg.add_training_data(anim, "intralobular1", 1, show=True)
        plt.figure()
        texseg.add_training_data(anim, "intralobular2", 1, show=True)
        # centers = texseg.get_tile_centers(anim, "intralobular1")
        # view1 = texseg.get_patch_view(anim, centers[0])
        # plt.imshow(view1.get_region_image())
        # view1 = texseg.get_patch_view(anim, centers[1])
        # plt.imshow(view1.get_region_image())
        # plt.show()
        plt.figure()
        # print("number of patches: {}".format(len(texseg.refs)))
        texseg.add_training_data(anim, "extralobular1", 2, show=True)
        plt.figure()
        texseg.add_training_data(anim, "extralobular3", 2, show=True)

        # print("number of patches: {}".format(len(texseg.refs)))

        texseg.show_tiles(anim, "intralobular1", [0, -1])
        # texseg.show_tiles(anim, "intralobular2", [0, -1])
        # texseg.show_tiles(anim, "extralobular1", [0, -1])
        texseg.show_tiles(anim, "extralobular3", [0, -1])
        # plt.show()
        logger.debug("number of patches: {}".format(len(texseg.data)))
        # texseg.add_training_data(anim, "obj3", 3)

        texseg.fit()
        views = anim.get_views_by_title("test3", level=texseg.level)
        texseg.predict(views[0], show=True)
        plt.savefig("segmentation.png")
        # plt.show()

    def test_texture_energy_on_lobulus(self):
        fn = io3d.datasets.join_path(
            "medical", "orig", "sample_data", "SCP003", "SCP003.ndpi", get_root=True
        )
        # fn = io3d.datasets.join_path("scaffold", "Hamamatsu", "PIG-008_P008 LL-P_HE_parenchyme perif..ndpi", get_root=True)
        anim = saim.AnnotatedImage(fn)

        texseg = satex.TextureSegmentation()

        # title = "test3"
        title = "test1"
        views = anim.get_views_by_title(title, level=texseg.level)
        energy = satex.tiles_processing(
            views[0].get_region_image(as_gray=True),
            fcn=satex.texture_energy,
            tile_spacing=texseg.tile_size,
        )
        # seg = texseg.predict(views[0], show=False, function=texture_energy)
        plt.figure(figsize=(10, 12))
        plt.subplot(211)
        img = views[0].get_region_image(as_gray=True)
        plt.imshow(img, cmap="gray")
        # plt.colorbar()
        plt.subplot(212)
        plt.imshow(energy)
        # plt.colorbar()
        plt.savefig("glcm_energy_{}.png".format(title))
        # plt.show()

    def test_texture_glcm_features_on_lobulus_by_tiles_processing(self):
        fn = io3d.datasets.join_path(
            "medical", "orig", "sample_data", "SCP003", "SCP003.ndpi", get_root=True
        )
        # fn = io3d.datasets.join_path("scaffold", "Hamamatsu", "PIG-008_P008 LL-P_HE_parenchyme perif..ndpi", get_root=True)
        anim = saim.AnnotatedImage(fn)

        texseg = satex.TextureSegmentation()
        texseg.set_tile_size(64)

        # title = "test3"
        title = "test2"
        # title = "test1"
        views = anim.get_views_by_title(title, level=texseg.level)
        energy = satex.tiles_processing(
            views[0].get_region_image(as_gray=True),
            fcn=lambda img: satex.texture_glcm_features(img, 32),
            tile_spacing=texseg.tile_size,
            fcn_output_n=3,
            dtype=None,
        )
        # seg = texseg.predict(views[0], show=False, function=texture_energy)
        plt.figure(figsize=(10, 12))
        plt.subplot(221)
        img = views[0].get_region_image()
        plt.imshow(img)
        plt.title("original image")
        plt.subplot(222)
        plt.title("GLCM energy")
        saim.imshow_with_colorbar(energy[:, :, 0])
        plt.subplot(223)
        plt.title("GLCM homogeneity")
        saim.imshow_with_colorbar(energy[:, :, 1])
        plt.subplot(224)
        plt.title("GLCM correlation")
        saim.imshow_with_colorbar(energy[:, :, 2])
        mx = np.max(energy, axis=(0, 1))
        mn = np.min(energy, axis=(0, 1))
        logger.debug(mx)
        # plt.colorbar()
        plt.savefig("glcm_features_{}.png".format(title))

        plt.figure()
        plt.imshow(energy)
        plt.savefig("glcm_features_color_{}.png".format(title))
        # plt.show()


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr)
    logger.setLevel(logging.DEBUG)
    unittest.main()
