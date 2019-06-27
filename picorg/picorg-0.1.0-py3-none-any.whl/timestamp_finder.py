from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

import exifread


def get_timestamp(filename):
    ts = PILWrapper.get_timestamp(filename)
    if ts is None:
        ts = ExifReadWrapper.get_timestamp(filename)
    return date_text_to_filename(ts) if ts is not None else None


def date_text_to_filename(date_text):
    try:
        return datetime.strptime(date_text, "%Y:%m:%d %H:%M:%S").strftime(
            "%Y%m%d_%H%M%S"
        )
    except ValueError:
        return None


class PILWrapper:
    @staticmethod
    def get_timestamp(filename):
        try:
            img = Image.open(filename)
            exif_data = None
            exif_data = img._getexif()
            if exif_data is None:
                return None
            field = PILWrapper.__get_field(exif_data, "DateTimeOriginal")

            if field is not None and date_text_to_filename(field[0]) is not None:
                return field[0]

            field = PILWrapper.__get_field(exif_data, "DateTimeDigitized")
            if field is not None and date_text_to_filename(field[0]) is not None:
                return field[0]
        except Exception as e:
            # print(e.__repr__())
            return None

    @staticmethod
    def __get_field(exif, field):
        for (k, v) in exif.items():
            # print(str(TAGS.get(k)) +": " +str(v))
            if TAGS.get(k) == field:
                return v
        return None


class ExifReadWrapper:
    @staticmethod
    def get_timestamp(filename):
        try:
            exif_data = None
            with open(filename, "rb") as f:
                tags = exifread.process_file(f)  # Return Exif tags
            field = ExifReadWrapper.__get_field(tags, "EXIF DateTimeDigitized")
            if field is None:
                return None

            return str(field)
        except Exception as e:
            # print(e.__repr__())
            return None

    @staticmethod
    def __get_field(exif, field):
        for (k, v) in exif.items():
            # print(str(k) +": " +str(v))
            if k == field:
                return v
        return None
