import os
from io import BytesIO

import PIL
from PIL import ImageDraw
from PIL import ImageFont

import numpy as np
import SimpleITK as sitk

from imageio import mimsave, volread, imread, imsave

from dtoolbioimage import ColorImage3D, Image
from dtoolbioimage.ipyutils import cached_segmentation_viewer
from dtoolbioimage.util.array import pretty_color_array, unique_color_array, color_array

from skimage.measure import regionprops
from skimage.morphology import dilation
from skimage.segmentation import find_boundaries

from scipy.ndimage.morphology import binary_erosion


def select_region(segmentation, label):
    by_label = {r.label: r for r in regionprops(segmentation)}

    rmin, cmin, zmin, rmax, cmax, zmax = by_label[label].bbox

    selected = segmentation[rmin:rmax, cmin:cmax, zmin:zmax]   

    return selected == label


def spherality(region):
    eroded = binary_erosion(region)
    surface = region ^ eroded

    S = np.sum(surface)
    V = np.sum(region)

    mult = 4.5 * np.sqrt(np.pi)

    return mult * V / np.power(S, 1.5)


class SegmentationHeatMapPalette(object):

    def __init__(self, label_value_map):
        values = label_value_map.values()
        self.min_val = min(values)
        self.max_val = max(values)

        self.label_value_map = label_value_map

        assert self.max_val - self.min_val > 0

    def get_rgb_color(self, value):

        normalised_val = (value - self.min_val) / (self.max_val - self.min_val)

        g = int(normalised_val * 255)
        r = 255 - g
        b = 0

        return r, g, b

    def __getitem__(self, key):

        default = [0, 0, 0]

        if key in self.label_value_map:
            value = self.label_value_map[key]
            return self.get_rgb_color(value)
        else:
            return default


def measure_by_label(segmentation, measurement_stack, l):
    region_coords = np.where(segmentation == l)
    value = sum(measurement_stack[region_coords])
    size = len(region_coords[0])
    return value / size


def rprops_by_label(label_image):
    return {r.label: r for r in regionprops(label_image)}

class Segmentation(np.ndarray):

    @classmethod
    def from_file(cls, fpath):

        unique_color_image = imread(fpath)

        rdim, cdim, _ = unique_color_image.shape

        segmentation = np.zeros((rdim, cdim), dtype=np.uint32).view(cls)
        segmentation += unique_color_image[:,:,2]
        segmentation += unique_color_image[:,:,1] * 256
        segmentation += unique_color_image[:,:,0] * 256 * 256

        segmentation._rprops = rprops_by_label(segmentation)

        return segmentation

    def _repr_png_(self):

        b = BytesIO()
        imsave(b, self.pretty_color_image, 'PNG', compress_level=0)

        return b.getvalue()

    @property
    def rprops(self):
        return self._rprops

    @property
    def pretty_color_image(self):

        return pretty_color_array(self)

    @property
    def unique_color_image(self):

        return unique_color_array(self)

    @property
    def centroids(self):
        rprops = regionprops(self)

        return [r.centroid for r in rprops]

    @property
    def labels(self):
        return set(np.unique(self)) - set([0])

    @property
    def label_id_image(self):

        fnt_size = 10
        drawimg = PIL.Image.fromarray(self.pretty_color_image)
        d = ImageDraw.Draw(drawimg)
        fnt = ImageFont.truetype('Microsoft Sans Serif.ttf', fnt_size)

        # Offsets
        xo = -fnt_size
        yo = -fnt_size

        for region in regionprops(self):
            y, x = map(int, region.centroid)
            d.text((x+xo, y+yo), str(region.label), font=fnt, fill=(255, 255, 255))

        return drawimg

    def save(self, fpath, encoding='rgb'):

        _, ext = os.path.splitext(fpath)
        assert ext in ['.tif', '.tiff']

        if encoding == 'rgb':
            uci = self.unique_color_image

        imsave(fpath, uci)

    def find_adjacent_labels(self, label):
        region_coords = self.rprops[label].coords
        region_only = np.zeros(self.shape, dtype=np.uint8)
        region_only[tuple(zip(*region_coords))] = 255
        boundaries = find_boundaries(region_only)
        dilated_boundaries = dilation(boundaries)

        return set(self[np.where(dilated_boundaries)]) - set([label])


class Segmentation3D(np.ndarray):

    def save(self, fpath, encoding='rgb'):

        _, ext = os.path.splitext(fpath)
        assert ext in ['.tif', '.tiff']

        if encoding == 'rgb':
            uci = self.unique_color_image
            transposed = np.transpose(uci, [2, 0, 1, 3])
        elif encoding == '32bit':
            transposed = np.transpose(self, [2, 0, 1])
        else:
            raise ValueError('Unknown encoding: {}'.format(encoding))

        mimsave(fpath, transposed)

    @property
    def unique_color_image(self):

        return unique_color_array(self)
    
    @property
    def pretty_color_image(self):

        return pretty_color_array(self)

    def _ipython_display_(self):

        if len(self.shape) == 2:
            display(self.pretty_color_image.view(Image))
            return

        display(cached_segmentation_viewer(self))

    @classmethod
    def from_file(cls, fpath):

        unique_color_image = volread(fpath)

        zdim, xdim, ydim, _ = unique_color_image.shape

        planes = []
        for z in range(zdim):
            segmentation = np.zeros((xdim, ydim), dtype=np.uint32)
            segmentation += unique_color_image[z,:,:,2]
            segmentation += unique_color_image[z,:,:,1] * 256
            segmentation += unique_color_image[z,:,:,0] * 256 * 256
            planes.append(segmentation)

        return np.dstack(planes).view(Segmentation3D)

    @property
    def labels(self):
        return set(np.unique(self)) - set([0])

    def region_in_bb(self, label):
        by_label = {r.label: r for r in regionprops(self)}

        rmin, cmin, zmin, rmax, cmax, zmax = by_label[label].bbox

        selected = self[rmin:rmax, cmin:cmax, zmin:zmax]

        return selected == label

    def make_heatmap(self, measure_stack):
        measures = {l: measure_by_label(self, measure_stack, l) for l in self.labels}

        palette = SegmentationHeatMapPalette(measures)

        return color_array(self, palette).view(ColorImage3D)

    def __len__(self):
        return len(self.labels)


def sitk_watershed_segmentation(stack, level=0.664):
    """Segment the given stack."""

    itk_im = sitk.GetImageFromArray(stack)
    median_filtered = sitk.Median(itk_im)
    grad_mag = sitk.GradientMagnitude(median_filtered)
    blurred = sitk.DiscreteGaussian(grad_mag, 2.0)
    segmentation = sitk.MorphologicalWatershed(blurred, level)
    relabelled = sitk.RelabelComponent(segmentation)

    return sitk.GetArrayFromImage(relabelled).view(Segmentation3D)


def filter_segmentation_by_size(segmentation, max_label):

    filtered = segmentation.copy()

    filtered[np.where(filtered > max_label)] = 0
    filtered[np.where(filtered < 3)] = 0

    return filtered.view(Segmentation3D)
