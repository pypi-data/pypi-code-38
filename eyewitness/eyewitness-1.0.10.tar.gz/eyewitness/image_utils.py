import os
import six
import requests
from abc import ABCMeta, abstractmethod

import numpy as np
import pkg_resources
import PIL
from eyewitness.config import (POST_PATH, POST_BYTES, RAW_IMAGE_PATH, IMAGE_ID)
from eyewitness.utils import make_path
from eyewitness.image_id import ImageId
from PIL import ImageFont, ImageDraw
DEFAULT_FONT_PATH = pkg_resources.resource_filename('eyewitness', 'font/FiraMono-Medium.otf')


class Image(object):
    def __init__(self, image_id, raw_image_path=None, pil_image_obj=None):
        """
        Image object is use to represent a Image in whole eyewitness project

        To initialize a Image obj, image_id is required, and one of raw_image_path,
        pil_image_obj should be given, while only giving raw_image_path is kind of lazy evaluation,
        will read the image only when image_obj.pil_image_obj called

        Parameters
        ----------
        image_id: ImageId
            the id of image

        raw_image_path: Optional[str]
            the raw image path

        pil_image_obj: Optional[PIL.Image.Image]
            the pil image obj
        """
        if not (raw_image_path or isinstance(pil_image_obj, PIL.Image.Image)):
            raise ValueError("there should be at least one way to generate the Pil image obj")
        self.raw_image_path = raw_image_path
        self._pil_image_obj = pil_image_obj
        self.image_id = image_id if isinstance(image_id, ImageId) else ImageId.from_str(image_id)

    @property
    def pil_image_obj(self):
        """
        pil_image_obj is a property of the Image, if _pil_image_obj exist will directly return the
        obj, else will read from raw_image_path.
        """
        if not isinstance(self._pil_image_obj, PIL.Image.Image):
            self._pil_image_obj = ImageHandler.read_image_file(self.raw_image_path)
        return self._pil_image_obj

    def fetch_bbox_pil_objs(self, bbox_objs):
        """
        Parameters
        ----------
        bbox_objs: List[BoundedBoxObject]
            List of bbox objs, which used to generate bbox pil_image_obj

        Returns:
        --------
        output_list: List[PIL.Image.Image]
        """
        output_list = []
        for bbox_obj in bbox_objs:
            cropped_img = self.pil_image_obj.crop([
                bbox_obj.x1, bbox_obj.y1, bbox_obj.x2, bbox_obj.y2])
            output_list.append(cropped_img)
        return output_list


class ImageHandler(object):
    """
    util functions for image processing
    including: save, read from file, read from bytes, draw bounding box.
    """
    @classmethod
    def save(cls, image, output_path):
        """

        Parameters
        ----------
        image: PIL.Image
            image obj
        output_path: str
            path to be save

        """
        if isinstance(output_path, ImageId):
            output_path = str(output_path)
        folder = os.path.dirname(output_path)
        if folder:
            make_path(folder)
        image.save(output_path)

    @classmethod
    def read_image_file(cls, image_path):
        """PIL.Image.open read from file.

        Parameters
        ----------
        image_path: str
            source image path

        Returns
        -------
        pil_image_obj: PIL.Image.Image
            PIL.Image.Image instance
        """
        return PIL.Image.open(image_path)

    @classmethod
    def read_image_bytes(cls, image_byte):
        """PIL.Image.open support BytesIO input.

        Parameters
        ----------
        image_path: BytesIO
            read image from ByesIO obj

        Returns
        -------
        pil_image_obj: PIL.Image.Image
            PIL.Image.Image instance
        """
        return PIL.Image.open(image_byte)

    @classmethod
    def draw_bbox(cls, image, detections, colors=None, font_path=DEFAULT_FONT_PATH):
        """draw bbox on to image.

        Parameters
        ----------
        image: PIL.Image.Image
            image to be draw
        detections: List[BoundedBoxObject]
            bbox to draw
        colors: Optional[dict]
            color to be used
        font_path: str
            font to be used

        """
        if colors is None:
            colors = {}

        font = ImageFont.truetype(
            font=font_path,
            size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        for (left, top, right, bottom, predicted_class, score, _) in detections:
            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            # creating bbox on images
            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=colors.get(predicted_class, 'red'))
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=colors.get(predicted_class, 'red'))
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)


@six.add_metaclass(ABCMeta)
class ImageProducer():
    """ImageProducer abstract class, should produce_method property and produce_image function
    """
    @property
    def produce_method(self):
        raise NotImplementedError

    @abstractmethod
    def produce_image(self):
        raise NotImplementedError


class PostFilePathImageProducer(ImageProducer):
    """PostFilePath Image Producer, will sent the image_path string to destination by Http post
    """
    def __init__(self, host, protocol='http'):
        self.protocol = protocol
        self.host = host

    @property
    def produce_method(self):
        return POST_PATH

    def produce_image(self, image_id, raw_image_path):
        headers = {IMAGE_ID: str(image_id),
                   RAW_IMAGE_PATH: raw_image_path}
        requests.post("%s://%s/detect_post_path" % (self.protocol, self.host), headers=headers)


class PostBytesImageProducer(ImageProducer):
    """PostBytes Image Producer, will sent the image bytes to destination by Http post
    """
    def __init__(self, host, protocol='http'):
        self.protocol = protocol
        self.host = host

    @property
    def produce_method(self):
        return POST_BYTES

    def produce_image(self, image_id, image_bytes, raw_image_path=None):
        headers = {IMAGE_ID: str(image_id)}

        if raw_image_path:
            headers[RAW_IMAGE_PATH] = raw_image_path

        requests.post(url="%s://%s/detect_post_bytes" % (self.protocol, self.host),
                      headers=headers,
                      data=image_bytes)


def swap_channel_rgb_bgr(image):
    """reverse the color channel image:
    convert image (w, h, c) with channel rgb -> bgr, bgr -> rgb.

    Parameters
    ----------
    image: np.array

    Returns
    -------
    image: np.array

    """
    image = image[:, :, ::-1]
    return image


def resize_and_stack_image_objs(resize_shape, pil_image_objs):
    """resize images and concat into numpy array

    Parameters
    ----------
    resize_shape: tuple[int]
        the target resize shape (w, h)
    pil_image_objs: List[PIL.Image.Image]
        List of image objs

    Returns
    -------
    batch_images_array: np.array with shape (n, w, h, c)
    """
    output = []
    for pil_image_obj in pil_image_objs:
        output.append(np.array(pil_image_obj.resize(resize_shape)))
    batch_images_array = np.stack(output, axis=0)
    return batch_images_array
