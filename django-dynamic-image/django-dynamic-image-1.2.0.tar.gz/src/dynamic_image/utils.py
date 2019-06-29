import os
import uuid
import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from image_tools.sizes import resize_and_crop

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
