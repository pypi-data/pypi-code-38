""" Functions facilitating file operations """

from hashlib import md5

__all__ = ["checksum"]


def checksum(path, blocksize=int(2e+9)):
    """
    Generate a md5 checksum for the file contents in the provided path.

    :param str path: path to file for which to generate checksum
    :param int blocksize: number of bytes to read per iteration, default: 2GB
    :return str: checksum hash
    """
    m = md5()
    with open(path, 'rb') as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()
