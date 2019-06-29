import os
import uuid
import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

try:
    from PIL import Image
except ImportError:
    import Image

ACCEPTED_FILE_FORMATS = ("gif", "png", "jpeg")


# TODO: Attempt to get format from end of url string.
def download_image_as(url, file_format, file_name=None):
    # Ensure the file format is lowercase.
    file_format = file_format.lower()
    # Ensure the file format doesnt starts with a period.
    if file_format.startswith("."):
        file_format = "".join(file_format.split(".")[1:])
    # Ensure the file format is one that we accept.
    if file_format not in ACCEPTED_FILE_FORMATS:
        raise Exception("Not an accepted format. ({})".format(file_format))
    # Ensure the url doesnt start with no protocol.
    if url.startswith("//"):
        url = url.split("//")[1]
    # Get the response data.
    response = requests.get("http://" + url)
    # If we failed to get a response, raise an exception.
    if response.status_code != 200:
        raise Exception("Failed to download image at url {}".format(url))
    # Create a new copy of the image we downloaded in memory.
    infile = Image.open(BytesIO(response.content))
    if infile.mode != "RGB":
        infile = infile.convert("RGB")
    outfile = BytesIO()
    # Save the memory file as a formatted image.
    infile.save(outfile, format=file_format.upper())
    # Create a universal fileanme if we don't get one to use.
    if file_name is None:
        file_name = "{prefix}.{suffix}".format(
            prefix=uuid.uuid4().hex, suffix=file_format
        )
    else:
        # Ensure the file name prefix is formatted appropriately.
        # Ensure the file name suffix is correct.
        bits = file_name.split(".")
        prefix_bits = bits[:-1]
        suffix = bits[-1]
        if suffix is not file_format:
            suffix = file_format
        file_name = "{}.{}".format("_".join(prefix_bits), suffix)
    # Create the content type string.
    content_type = "image/{}".format(file_format)
    # Get the byte size.
    content_length = outfile.getbuffer().nbytes
    return InMemoryUploadedFile(
        outfile, None, file_name, content_type, content_length, None
    )


def download_image_as_gif(url, file_name=None):
    return download_image_as(url, "GIF", file_name)


def download_image_as_jpeg(url, file_name=None):
    return download_image_as(url, "JPEG", file_name)


def download_image_as_png(url, file_name=None):
    return download_image_as(url, "PNG", file_name)


def resize_and_crop(path, size, crop_origin="middle"):
    """
    Resize and crop an image to fit the specified size.

    args:
    path: path for the image to resize.
    size: `(width, height)` tuple.
    crop_origin: can be 'top', 'middle' or 'bottom', depending on this
    value, the image will cropped getting the 'top/left', 'middle' or
    'bottom/right' of the image to fit the size.
    raises:
    Exception: if can not open the file in img_path of there is problems
    to save the image.
    ValueError: if an invalid `crop_origin` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(path)
    # Convert the image to palette mode (for JPEG)
    if img.mode != "RGB":
        img = img.convert("RGB")
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    # The image is scaled/cropped vertically or horizontally depending on the
    # ratio.
    if ratio > img_ratio:
        img = img.resize(
            (size[0], int(round(size[0] * img.size[1] / img.size[0]))), Image.ANTIALIAS
        )
        # Crop in the top, middle or bottom
        if crop_origin == "top":
            box = (0, 0, img.size[0], size[1])
        elif crop_origin == "middle":
            box = (
                0,
                int(round((img.size[1] - size[1]) / 2)),
                img.size[0],
                int(round((img.size[1] + size[1]) / 2)),
            )
        elif crop_origin == "bottom":
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else:
            raise ValueError("ERROR: invalid value for crop_origin")
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize(
            (int(round(size[1] * img.size[0] / img.size[1])), size[1]), Image.ANTIALIAS
        )
        # Crop in the top, middle or bottom
        if crop_origin == "top":
            box = (0, 0, size[0], img.size[1])
        elif crop_origin == "middle":
            box = (
                int(round((img.size[0] - size[0]) / 2)),
                0,
                int(round((img.size[0] + size[0]) / 2)),
                img.size[1],
            )
        elif crop_origin == "bottom":
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else:
            raise ValueError("ERROR: invalid value for crop_origin")
        img = img.crop(box)
    else:
        img = img.resize((size[0], size[1]), Image.ANTIALIAS)
    return img


# NOTE: This will resize smaller images and, while it respects aspect
#       ratios, make the resoution worse.
def get_resized_image_file(image_field, image_format, dimensions, crop_origin="middle"):
    # Generate the resize image file.
    image_file = resize_and_crop(image_field.file, dimensions, crop_origin)
    # Create a new file object.
    image_bytes = BytesIO()
    image_file.save(image_bytes, image_format)
    image_bytes.seek(0)
    # Create the filename
    image_basename = os.path.basename(image_field.name)
    image_basename_bits = image_basename.split(".")
    image_filename_prefix = "_".join(image_basename_bits[:-1])
    image_filename = "{}_{}x{}.{}".format(
        image_filename_prefix, dimensions[0], dimensions[1], image_format
    )
    # Return the file object to save to the ImageField.
    return SimpleUploadedFile(
        image_filename, image_bytes.read(), content_type="image/{}".format(image_format)
    )
