import zipfile
import os
from shutil import copyfile
from enum import Enum
import gzip
from thompcoutils import log_utils
import logging


class ZipException(Exception):
    pass


class ZipType(Enum):
    ZIP = 1
    GZIP = 2


def zip_file(from_file, to_file=None, overwrite=False, method=ZipType.ZIP):
    if to_file is None:
        if method == ZipType.ZIP:
            extension = ".zip"
        elif method == ZipType.GZIP:
            extension = ".gz"
        else:
            raise ZipException("Method {} is not supported".format(str(method)))
        to_file = os.path.splitext(from_file)[0] + extension
    if os.path.isfile(to_file) and not overwrite:
        raise ZipException("{} exists".format(to_file))
    if method == ZipType.ZIP:
        # noinspection PyBroadException
        try:
            compression = zipfile.ZIP_DEFLATED
        except Exception:
            compression = zipfile.ZIP_STORED
        zf = zipfile.ZipFile(to_file, mode='w')
        try:
            zf.write(from_file, compress_type=compression)
        finally:
            zf.close()
    elif method == ZipType.GZIP:
        with open(from_file, 'rb') as orig_file:
            with gzip.open(to_file, 'wb') as zipped_file:
                zipped_file.writelines(orig_file)
    else:
        raise ZipException("Method {} is not supported".format(str(method)))
    return to_file


def test_zip(original_file, target_file=None, method=None, extension=None):
    logger = log_utils.get_logger()
    if target_file is None:
        zipped_file = os.path.splitext(original_file)[0] + extension
        if os.path.isfile(zipped_file):
            os.remove(zipped_file)
        completed_file = zip_file(original_file, method=method)
        if zipped_file != completed_file:
            raise Exception("{} is not the same as {}".format(zipped_file, completed_file))
        logger.debug("{} zipped to {}".format(original_file, completed_file))
        try:
            zip_file(original_file, method=method)
            raise Exception("Should not be able to overwrite existing file {}".format(zipped_file))
        except ZipException:
            pass
        completed_file = zip_file(original_file, overwrite=True, method=method)
        if zipped_file != completed_file:
            raise Exception("{} is not the same as {}".format(zipped_file, completed_file))
        os.remove(zipped_file)
    else:
        if os.path.isfile(target_file):
            os.remove(target_file)
        completed_file = zip_file(original_file, target_file, method=method)
        if target_file != completed_file:
            raise Exception("{} is not the same as {}".format(target_file, completed_file))
        logger.debug("{} zipped to {}".format(original_file, completed_file))
        try:
            zip_file(original_file, target_file, method=method)
            raise Exception("Should not be able to overwrite existing file {}".format(target_file))
        except ZipException:
            pass
        completed_file = zip_file(original_file, target_file, overwrite=True, method=method)
        if target_file != completed_file:
            raise Exception("{} is not the same as {}".format(target_file, completed_file))
        os.remove(target_file)


def main():
    logger = log_utils.get_logger()
    for method in ZipType:
        logger.debug("Testing {}".format(method))
        if method == ZipType.ZIP:
            extension = ".zip"
        elif method == ZipType.GZIP:
            extension = ".gz"
        else:
            raise Exception("Untested extension {}".format(method))
        original_file = os.path.basename(__file__)
        zipped_file = os.path.splitext(original_file)[0] + "1" + extension
        test_zip(original_file, method=method, extension=extension)
        test_zip(original_file, zipped_file, method=method, extension=extension)
        tmp_file = os.path.join("/tmp", original_file)
        zipped_file = os.path.splitext(tmp_file)[0] + "1" + extension
        copyfile(original_file, tmp_file)
        test_zip(tmp_file, method=method, extension=extension)
        test_zip(tmp_file, zipped_file, method=method, extension=extension)
        os.remove(tmp_file)


if __name__ == "__main__":
    log_configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
    logging.config.fileConfig(log_configuration_file)
    main()
