# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modul is used for slice image and view processing. It cooperates with openslide.
Some of coordinates are swapped. It is due to openslide. With request subimage with size=[A, B] it will
return subimage with shape [B, A]. It is probably because of visualization.
"""

from loguru import logger
# problem is loading lxml together with openslide
# from lxml import etree
from typing import List
import os.path as op
import glob
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import skimage.color
from scaffan import annotation as scan
from scaffan import libfixer
import imma

from matplotlib.path import Path as mplPath
from mpl_toolkits.axes_grid1 import make_axes_locatable


#


def import_openslide():

    pth = op.expanduser(r"~\Downloads\openslide-win64-20171122\bin")
    dll_list = glob.glob(op.join(pth, "*.dll"))
    if len(dll_list) < 5:
        print("Trying to download openslide dll files in {}".format(pth))
        libfixer.libfix()
    # pth = op.expanduser(r"~\projects\scaffan\devel\knihovny")
    # pth = op.expanduser(r"~\Miniconda3\envs\lisa36\Library\bin")
    sys.path.insert(0, pth)
    orig_PATH = os.environ["PATH"]
    orig_split = orig_PATH.split(";")
    if pth not in orig_split:
        print("add path {}".format(pth))
    os.environ["PATH"] = pth + ";" + os.environ["PATH"]


import_openslide()
import openslide


# def
def get_image_by_center(imsl, center, level=3, size=None, as_gray=True):
    if size is None:
        size = np.array([800, 800])

    location = get_region_location_by_center(imsl, center, level, size)

    imcr = imsl.read_region(location, level=level, size=size)
    im = np.asarray(imcr)
    if as_gray:
        im = skimage.color.rgb2gray(im)
    return im


def get_region_location_by_center(imsl, center, level, size):
    size2 = (size / 2).astype(int)

    offset = size2 * imsl.level_downsamples[level]
    location = (np.asarray(center) - offset).astype(np.int)
    return location


def get_region_center_by_location(imsl, location, level, size):
    size2 = (size / 2).astype(int)

    offset = size2 * imsl.level_downsamples[level]
    center = (np.asarray(location) + offset).astype(np.int)
    return center


def get_pixelsize(imsl, level=0, requested_unit="mm"):
    """
    imageslice
    :param imsl: image slice obtained by openslice.OpenSlide(path)
    :return: pixelsize, pixelunit
    """
    pm = imsl.properties
    resolution_unit = pm.get("tiff.ResolutionUnit")
    resolution_x = pm.get("tiff.XResolution")
    resolution_y = pm.get("tiff.YResolution")
    #     print("Resolution {}x{} pixels/{}".format(resolution_x, resolution_y, resolution_unit))
    downsamples = imsl.level_downsamples[level]

    input_resolution_unit = resolution_unit
    if resolution_unit is None:
        pixelunit = resolution_unit
    elif requested_unit in ("mm"):
        if resolution_unit in ("cm", "centimeter"):
            downsamples = downsamples * 10.0
            pixelunit = "mm"
        elif resolution_unit in ("mm"):
            pixelunit = resolution_unit
        else:
            raise ValueError(
                "Cannot covert from {} to {}.".format(
                    input_resolution_unit, requested_unit
                )
            )
    else:
        raise ValueError(
            "Cannot covert from {} to {}.".format(input_resolution_unit, requested_unit)
        )

    # if resolution_unit != resolution_unit:
    #     raise ValueError("Cannot covert from {} to {}.".format(input_resolution_unit, requested_unit))

    pixelsize = np.asarray(
        [downsamples / float(resolution_x), downsamples / float(resolution_y)]
    )

    return pixelsize, pixelunit


def get_offset_px(imsl):

    pm = imsl.properties
    pixelsize, pixelunit = get_pixelsize(imsl)
    offset = np.asarray(
        (
            int(pm["hamamatsu.XOffsetFromSlideCentre"]),
            int(pm["hamamatsu.YOffsetFromSlideCentre"]),
        )
    )
    # resolution_unit = pm["tiff.ResolutionUnit"]
    offset_mm = offset * 0.000001
    if pixelunit is not "mm":
        raise ValueError("Cannot convert pixelunit {} to milimeters".format(pixelunit))
    offset_from_center_px = offset_mm / pixelsize
    im_center_px = np.asarray(imsl.dimensions) / 2.0
    offset_px = im_center_px - offset_from_center_px
    return offset_px


def get_resize_parameters(imsl, former_level, former_size, new_level):
    """
    Get scale factor and size of image on different level.

    :param imsl: OpenSlide
    :param former_level: int
    :param former_size: list of ints
    :param new_level: int
    :return: scale_factor, new_size
    """
    scale_factor = (
        imsl.level_downsamples[former_level] / imsl.level_downsamples[new_level]
    )
    new_size = (np.asarray(former_size) * scale_factor).astype(np.int)
    return scale_factor, new_size


class AnnotatedImage:
    def __init__(self, path, skip_read_annotations=False):
        logger.debug("Reading file {}".format(path))
        self.path = path
        self.openslide = openslide.OpenSlide(path)
        self.region_location = None
        self.region_size = None
        self.region_level = None
        self.region_pixelsize = None
        self.region_pixelunit = None
        self.pixelunit = "mm"
        self.level_pixelsize = [
            get_pixelsize(self.openslide, i, requested_unit=self.pixelunit)[0]
            for i in range(0, self.openslide.level_count)
        ]
        if not skip_read_annotations:
            logger.debug("Reading the annotation")
            self.read_annotations()

    def get_file_info(self):
        pxsz, unit = self.get_pixel_size(0)
        # self.titles
        # self.colors
        return "Pixelsize: {}x{} [{}], {} annotations".format(pxsz[0], pxsz[1], unit, len(self.id_by_colors))

    def get_optimal_level_for_fluent_resize(self, pixelsize_mm, safety_bound=2):
        if np.isscalar(pixelsize_mm):
            pixelsize_mm = [pixelsize_mm, pixelsize_mm]
        pixelsize_mm = np.asarray(pixelsize_mm)


        pixelsize_mm2 = pixelsize_mm / safety_bound
        best_level = 0
        # scale_factor = None
        for i, pxsz in enumerate(self.level_pixelsize):
            if np.array_equal(pxsz, pixelsize_mm):
                best_level = i
                # scale_factor = 1.0
            elif all(pxsz < pixelsize_mm2):
                best_level = i

        return best_level

    def get_resize_parameters(self, former_level, former_size, new_level):
        """
        Get scale and size of image after resize to other level
        :param former_level:
        :param former_size:
        :param new_level:
        :return: scale_factor, new_size
        """
        return get_resize_parameters(
            self.openslide, former_level, former_size, new_level
        )

    def get_offset_px(self):
        return get_offset_px(self.openslide)

    def get_pixel_size(self, level=0):
        return self.level_pixelsize[level], self.pixelunit
        # return get_pixelsize(self.openslide, level)

    def get_image_by_center(self, center, level=3, size=None, as_gray=True):
        return get_image_by_center(self.openslide, center, level, size, as_gray)

    def get_region_location_by_center(self, center, level, size):
        return get_region_location_by_center(self.openslide, center, level, size)

    def get_region_center_by_location(self, location, level, size):
        return get_region_center_by_location(self.openslide, location, level, size)

    def read_annotations(self):
        self.annotations = scan.read_annotations(self.path)
        self.annotations = scan.annotations_to_px(self.openslide, self.annotations)
        self.id_by_titles = scan.annotation_titles(self.annotations)
        self.id_by_colors = scan.annotation_colors(self.annotations)
        # self.details = scan.annotation_details(self.annotations)
        return self.annotations

    def get_view(
            self, center=None, level=0, size_on_level=None,
            location=None, size_mm=None, pixelsize_mm=None, safety_bound=2) -> "View":
        view = View(
            anim=self, center=center, level=level, size_on_level=size_on_level,
            location=location, size_mm=size_mm, pixelsize_mm=pixelsize_mm, safety_bound=safety_bound
            )
        return view

    def get_views_by_title(self, title=None, level=2, return_ids=False, **kwargs) -> List['View']:
        annotation_ids = self.get_annotation_ids(title)
        if return_ids:
            return self.get_views(annotation_ids, level=level, **kwargs), annotation_ids
        else:
            return self.get_views(annotation_ids, level=level, **kwargs)

    def select_inner_annotations(self, id, color=None, raise_exception_if_not_found=False):
        if color is not None:
            an_ids_sel1 = self.select_annotations_by_color(color, raise_exception_if_not_found=raise_exception_if_not_found)
        else:
            an_ids_sel1 = list(self.annotations.keys())

        x_px = self.annotations[id]["x_px"]
        y_px = self.annotations[id]["y_px"]
        ids = []
        for idi in an_ids_sel1:
            ann = self.annotations[idi]
            x_pxi = ann["x_px"]
            y_pxi = ann["y_px"]

            if (
                    np.max(x_pxi) < np.max(x_px) and np.max(y_pxi) < np.max(y_px) and
                    np.min(x_px) < np.min(x_pxi) and np.min(y_px) < np.min(y_pxi)
            ):
                ids.append(idi)
        return ids

    def select_outer_annotations(self, id, color=None, raise_exception_if_not_found=False):
        if color is not None:
            an_ids_sel1 = self.select_annotations_by_color(color, raise_exception_if_not_found=raise_exception_if_not_found)
        else:
            an_ids_sel1 = list(self.annotations.keys())

        x_px = self.annotations[id]["x_px"]
        y_px = self.annotations[id]["y_px"]
        ids = []
        for idi in an_ids_sel1:
            ann = self.annotations[idi]
            x_pxi = ann["x_px"]
            y_pxi = ann["y_px"]

            if (
                    np.max(x_px) < np.max(x_pxi) and np.max(y_px) < np.max(y_pxi) and
                    np.min(x_pxi) < np.min(x_px) and np.min(y_pxi) < np.min(y_px)
            ):
                ids.append(idi)
        return ids

    def select_annotations_by_title(self, title):
        return self.get_annotation_ids(title)
        # return self.get_views(annotation_ids, level=level, **kwargs), annotation_ids


    def get_views(
        self,
        annotation_ids=None,
        level=None,
        margin=0.5,
        margin_in_pixels: bool=False,
        show=False,
        pixelsize_mm=None,
        safety_bound=2
    ) -> List["View"]:
        """

        :param annotation_ids:
        :param level: If neither level neither pixelsize_mm is set the level is set to 0
        :param margin: based on "margin_in_pixels" the margin in pixels(accoarding to the requested level) are used or
        margin is proportional to size of annotation object.
        :param margin_in_pixels: bool
        :param show:
        :return:
        """
        if pixelsize_mm is not None:
            level = self.get_optimal_level_for_fluent_resize(pixelsize_mm, safety_bound=safety_bound)
        if level is None:
            level = 0
        views = [None] * len(annotation_ids)
        for i, annotation_id in enumerate(annotation_ids):
            center, size = self.get_annotations_bounds_px(annotation_id)
            if margin_in_pixels:
                margin_px = int(margin)
            else:
                margin_px = (size * margin).astype(
                    np.int
                ) / self.openslide.level_downsamples[level]
            region_size = (
                (size / self.openslide.level_downsamples[level]) + 2 * margin_px
            ).astype(int)
            view = self.get_view(center=center, level=level, size_on_level=region_size,
                                 pixelsize_mm=pixelsize_mm)
            if show:
                view.region_imshow_annotation(annotation_id)
            views[i] = view

        return views

    def set_region(self, center=None, level=0, size=None, location=None):

        if size is None:
            size = [256, 256]

        size = np.asarray(size)

        if location is None:
            location = self.get_region_location_by_center(center, level, size)
        else:
            center = self.get_region_center_by_location(location, level, size)

        self.region_location = location
        self.region_center = center
        self.region_size = size
        self.region_level = level
        self.region_pixelsize, self.region_pixelunit = self.get_pixel_size(level)
        self.level_pixelsize = [
            get_pixelsize(
                self.openslide,
                level=i,
                requested_unit=self.region_pixelunit)[0]
            for i in range(0, self.openslide.level_count)
        ]
        scan.adjust_annotation_to_image_view(
            self.openslide, self.annotations, center, level, size
        )

    def select_annotations_by_color(self, id, raise_exception_if_not_found=True):
        if id is None:
            # probably should return all ids for all colors
            raise ColorError()
            return None

        if type(id) is str:
            if id not in self.id_by_colors:
                if raise_exception_if_not_found:
                    raise ColorError()
                return None
            id = self.id_by_colors[id]
        else:
            id = [id]
        return id

    def get_annotation_ids(self, id):
        if type(id) is str:
            id = self.id_by_titles[id]
        else:
            id = [id]
        return id

    def get_annotation_id(self, i):
        if type(i) is str:
            i = self.id_by_titles[i][0]
        return i

    def set_region_on_annotations(self, i=None, level=2, boundary_px=10, show=False):
        """

        :param i: index of annotation or annotation title
        :param level:
        :param boundary_px:
        :return:
        """
        i = self.get_annotation_id(i)
        center, size = self.get_annotations_bounds_px(i)
        region_size = (
            (size / self.openslide.level_downsamples[level]) + 2 * boundary_px
        ).astype(int)
        self.set_region(center=center, level=level, size=region_size)
        if show:
            self.region_imshow_annotation(i)

    def get_annotations_bounds_px(self, i=None):
        """
        Bounds are in pixels on level 0.
        :param i:
        :return:
        """
        i = self.get_annotation_id(i)
        if i is not None:
            anns = [self.annotations[i]]

        x_px = []
        y_px = []

        for ann in anns:
            x_px.append(ann["x_px"])
            y_px.append(ann["y_px"])

        mx = np.array([np.max(x_px), np.max(y_px)])
        mi = np.array([np.min(x_px), np.min(y_px)])
        all = [mi, mx]
        center = np.mean(all, 0)
        size = mx - mi
        return center, size

    def get_region_image(self, as_gray=False, as_unit8=False):
        imcr = self.openslide.read_region(
            self.region_location, level=self.region_level, size=self.region_size
        )
        im = np.asarray(imcr)
        if as_gray:
            im = skimage.color.rgb2gray(im)
            if as_unit8:
                im = (im * 255).astype(np.uint8)
        return im

    def plot_annotations(self, annotation_id=None):
        if annotation_id is None:
            anns = self.annotations
        else:
            annotation_id = self.get_annotation_id(annotation_id)
            anns = [self.annotations[annotation_id]]
        scan.plot_annotations(anns, in_region=True)

    def get_annotation_region_raster(self, i):
        i = self.get_annotation_id(i)
        polygon_x = self.annotations[i]["region_x_px"]
        polygon_y = self.annotations[i]["region_y_px"]
        polygon = list(zip(polygon_y, polygon_x))
        poly_path = mplPath(polygon)

        x, y = np.mgrid[: self.region_size[1], : self.region_size[0]]
        coors = np.hstack(
            (x.reshape(-1, 1), y.reshape(-1, 1))
        )  # coors.shape is (4000000,2)

        mask = poly_path.contains_points(coors)
        mask = mask.reshape(self.region_size[::-1])
        return mask

    def region_imshow_annotation(self, i):
        region = self.get_region_image()
        plt.imshow(region)
        self.plot_annotations(i)

    def coords_region_px_to_global_px(self, points_view_px):
        """
        :param points_view_px: [[x0, x1, ...], [y0, y1, ...]]
        :return:
        """

        px_factor = self.openslide.level_downsamples[self.region_level]
        print(px_factor)
        x_px = self.region_location[0] + points_view_px[0] * px_factor
        y_px = self.region_location[1] + points_view_px[1] * px_factor

        return x_px, y_px

    def coords_global_px_to_view_px(self, points_glob_px):
        """
        :param points_glob_px: [[x0, x1, ...], [y0, y1, ...]]
        :return:
        """

        px_factor = self.openslide.level_downsamples[self.region_level]
        print(px_factor)
        x_glob_px = points_glob_px[0]
        y_glob_px = points_glob_px[1]
        x_view_px = (x_glob_px - self.region_location[0]) / px_factor
        y_view_px = (y_glob_px - self.region_location[1]) / px_factor

        return x_view_px, y_view_px


class View:
    def __init__(self, anim: AnnotatedImage, center=None, level=0, size_on_level=None, location=None, size_mm=None, pixelsize_mm=None, safety_bound=2):
        self.anim: AnnotatedImage = anim
        self.set_region(center=center, level=level, size_on_level=size_on_level, location=location, size_mm=size_mm, pixelsize_mm=pixelsize_mm, safety_bound=safety_bound)

    def set_region(self, center=None, level=None, size_on_level=None, location=None, size_mm=None, pixelsize_mm=None, safety_bound=2):
        if (level is None) and (size_on_level is not None):
                raise ValueError("Parameter 'size_on_level' cannot be used if 'level' is not defined")
        if pixelsize_mm is not None:
            self.is_resized_by_pixelsize = True
            if np.isscalar(pixelsize_mm):
                pixelsize_mm = [pixelsize_mm, pixelsize_mm]
            pixelsize_mm = np.asarray(pixelsize_mm)
            self.region_pixelsize  = pixelsize_mm
            self.region_pixelunit = "mm"
            if level is None:
                level = self.anim.get_optimal_level_for_fluent_resize(self.region_pixelsize, safety_bound=safety_bound)

        else:
            if level is None:
                level = 0
            self.is_resized_by_pixelsize = False
            # self.region_pixelsize = None
            # self.region_pixelunit = "mm"
            self.region_pixelsize, self.region_pixelunit = self.get_pixelsize_on_level(level)

        if size_mm is not None:
            if np.isscalar(size_mm):
                size_mm = [size_mm, size_mm]
            if size_on_level is not None:
                raise ValueError("Parameter size and size_mm are exclusive.")
            size_mm = np.asarray(size_mm)
            size_on_level = np.ceil(size_mm / self.get_pixelsize_on_level(level)[0]).astype(np.int)

        if size_on_level is None:
            size_on_level = [256, 256]

        size_on_level = np.asarray(size_on_level)
        self.region_level = level
        self.region_size_on_level = size_on_level

        if pixelsize_mm is not None:
            pxsz = self.get_pixelsize_on_level(level)[0]
            self.zoom = pxsz/ (1.0 * pixelsize_mm)
            self.region_size_on_pixelsize_mm = np.ceil(size_on_level * self.zoom).astype(np.int)
        else:
            self.region_size_on_pixelsize_mm = size_on_level
            self.zoom = np.array([1, 1])

        if location is None:
            location = self.get_region_location_by_center(center, level, size_on_level)
        else:
            center = self.get_region_center_by_location(location, level, size_on_level)

        self.region_location = location
        self.region_center = center

        import copy

        self.annotations = copy.deepcopy(self.anim.annotations)
        scan.adjust_annotation_to_image_view(
            self.anim.openslide, self.annotations, center, level, size_on_level
        )

    def get_pixelsize_on_level(self, level=None):
        if level is None:
            level = self.region_level
        return self.anim.get_pixel_size(level)

    def mm_to_px(self, mm):
        pxsz, unit = self.get_pixelsize_on_level()
        return mm / pxsz


    def region_imshow_annotation(self, i):
        region = self.get_region_image()
        plt.imshow(region)
        self.plot_annotations(i)

    def coords_glob_px_to_view_px(self, x_glob_px, y_glob_px):
        # px_factor = self.anim.openslide.level_downsamples[self.region_level]
        px_factor = self.region_pixelsize / self.get_pixelsize_on_level(0)[0]

        x_px = (x_glob_px - self.region_location[0]) / px_factor[0]
        y_px = (y_glob_px - self.region_location[1]) / px_factor[1]

        return x_px, y_px

    def coords_view_px_to_glob_px(self, x_view_px, y_view_px):
        """
        :param x_view_px: [x0, x1, ...]
        :param y_view_px: [y0, y1, ...]]
        :return:
        """
        px_factor = self.anim.openslide.level_downsamples[self.region_level]
        # print(px_factor)
        x_px = self.region_location[0] + x_view_px * px_factor
        y_px = self.region_location[1] + y_view_px * px_factor

        return x_px, y_px

    def plot_points(self, x_glob_px, y_glob_px):
        # points = [x_glob_px, y_glob_px]
        x_view_px, y_view_px = self.coords_glob_px_to_view_px(x_glob_px, y_glob_px)
        plt.plot(x_view_px, y_view_px, "oy")

    def get_annotation_region_raster(self, annotation_id):
        annotation_id = self.anim.get_annotation_id(annotation_id)
        # Coordinates swap
        # coordinates are swapped here. Probably it is because Path uses different order from Image
        polygon_x = self.annotations[annotation_id]["region_x_px"] * self.zoom[0]
        polygon_y = self.annotations[annotation_id]["region_y_px"] * self.zoom[1]
        polygon = list(zip(polygon_y, polygon_x))
        poly_path = mplPath(polygon)

        # coordinates are swapped also here
        # x, y = np.mgrid[: self.region_size_on_level[1], : self.region_size_on_level[0]]
        x, y = np.mgrid[: self.region_size_on_pixelsize_mm[1], : self.region_size_on_pixelsize_mm[0]]
        coors = np.hstack(
            (x.reshape(-1, 1), y.reshape(-1, 1))
        )  # coors.shape is (4000000,2)

        mask = poly_path.contains_points(coors)
        mask = mask.reshape(self.region_size_on_pixelsize_mm[::-1])
        return mask

    def region_imshow_annotation(self, i):
        region = self.get_region_image()
        plt.imshow(region)
        self.plot_annotations(i)
        self.add_ticks()

    def add_ticks(self):
        locs, labels = plt.xticks()
        in_mm = locs * self.region_pixelsize[0]
        labels = ["{:.1e}".format(i) for i in in_mm]
        plt.xticks(locs, labels, rotation="vertical")

        locs, labels = plt.yticks()
        labels = ["{:.1e}".format(i * self.region_pixelsize[1]) for i in locs]
        plt.yticks(locs, labels)

    def plot_annotations(self, i=None):
        if i is None:
            anns = self.annotations
        else:
            i = self.anim.get_annotation_id(i)
            anns = [self.annotations[i]]
        scan.plot_annotations(anns, in_region=True, factor=self.zoom)

    def get_region_location_by_center(self, center, level, size):
        return get_region_location_by_center(self.anim.openslide, center, level, size)

    def get_region_center_by_location(self, location, level, size):
        return get_region_center_by_location(self.anim.openslide, location, level, size)

    # def get_region_image(self, as_gray=False):
    #     imcr = self.openslide.read_region(
    #         self.region_location, level=self.region_level, size=self.region_size_on_level
    #     )
    #     im = np.asarray(imcr)
    #     if as_gray:
    #         im = skimage.color.rgb2gray(im)
    #     return im

    def get_region_image_resolution(self, resolution_mm, as_gray=False, ):
        self.anim.openslide.level_downsamples

    def get_region_image(self, as_gray=False):
        """
        Get raster image from the view. It can have defined pixelsize, and also the level
        :param as_gray:
        :param pixelsize_mm:
        :param safety_bound: Resize safety multiplicator. If set to 2 it means to have at least 2 samples per pixel
        along each axis.
        :param level: The level of output image can be controled by this parameter. The computation of optimal level
        can be skipped by this.
        :return:
        """
        # if (level is None) and (pixelsize_mm is not None):
        #     level = self.anim.get_optimal_parameters_for_fluent_resize(pixelsize_mm, safety_bound=safety_bound)
        #     size = self.get_size_on_level(level)
        # else:
        #     level = self.region_level
        #     size = self.region_size_on_level

        imcr = self.anim.openslide.read_region(
            self.region_location, level=self.region_level, size=self.region_size_on_level
        )
        im = np.asarray(imcr)
        if as_gray:
            im = skimage.color.rgb2gray(im)

        if self.is_resized_by_pixelsize:
            pxsz_level, pxunit_level = self.anim.get_pixel_size(level=self.region_level)

            # im1 = imma.image.resize_to_mm(im, pxsz_level, self.region_pixelsize)
            # swap coordinates because openslice output image have swapped image coordinates
            im = imma.image.resize_to_mm(im, pxsz_level[::-1], self.region_pixelsize[::-1])


        return im

    def imshow(self, as_gray=False):
        plt.imshow(self.get_region_image(as_gray=as_gray))

    def get_size_on_level(self, new_level):
        imsl = self.anim.openslide
        former_level = self.region_level
        former_size = self.region_size_on_level
        scale_factor = (
            imsl.level_downsamples[former_level] / imsl.level_downsamples[new_level]
        )
        new_size = (np.asarray(former_size) * scale_factor).astype(np.int)

        return new_size

    def get_size_on_pixelsize_mm(self):
        return self.region_size_on_pixelsize_mm

    def to_level(self, new_level):
        size = self.get_size_on_level(new_level)
        newview = View(
            self.anim, location=self.region_location, size_on_level=size, level=new_level
        )
        return newview

    def to_pixelsize(self, pixelsize_mm, safety_bound=2.):
        level = self.anim.get_optimal_level_for_fluent_resize(pixelsize_mm, safety_bound=safety_bound)
        size = self.get_size_on_level(level)
        newview = View(
            self.anim, location=self.region_location, size_on_level=size, level=level, pixelsize_mm=pixelsize_mm
        )
        return newview

    def get_slices_for_insert_image_from_view(self, other_view: "View"):
        """
        Prepare region slice for inserting small image into current view.
        :param other_view:
        :return:
        """
        pixelsize_factor = self.get_pixelsize_on_level(0)[0] / self.region_pixelsize
        delta_px = ((other_view.region_location - self.region_location) * pixelsize_factor).astype(np.int)
        # start = (self.region_location + delta_px)[::-1]
        # delta_size_px = (other_view.get_size_on_pixelsize_mm() * pixelsize_factor).astype(np.int)
        start=delta_px[::-1]
        import imma.image
        pxsz1 = self.region_pixelsize[:2]
        pxsz2 = other_view.region_pixelsize[:2]
        stop = start + imma.image.calculate_new_shape(
            other_view.get_size_on_pixelsize_mm()[::-1],
            voxelsize_mm=pxsz2[::-1],
            new_voxelsize_mm=pxsz1[::-1]
        )
        return (slice(start[0], stop[0], 1), slice(start[1], stop[1],1))

    def insert_image_from_view(self, other_view: "View", img, other_img):
        """
        Put small image from different view into current image. Current image should be bigger.

        :param other_view:
        :param img:
        :param other_img:
        :return:
        """

        pxsz1 = self.region_pixelsize[:2]
        pxsz2 = other_view.region_pixelsize[:2]
        resized_other_img = imma.image.resize_to_mm(
            other_img,
            voxelsize_mm=pxsz2[::-1],
            new_voxelsize_mm=pxsz1[::-1]
        )

        sl = self.get_slices_for_insert_image_from_view(other_view)

        img[sl] = resized_other_img
        return img


class ColorError(Exception):
    pass



def imshow_with_colorbar(*args, **kwargs):
    ax = plt.gca()
    im = ax.imshow(*args, **kwargs)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)
