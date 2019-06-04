# coding=utf-8
from __future__ import absolute_import, print_function

import cv2
import imageio

from suanpan import asyncio, path
from suanpan.utils import convert


def _save(file, image):
    path.safeMkdirsForFile(file)
    cv2.imwrite(file, image)  # pylint: disable-msg=e1101
    return file


def _saveflat(file, data):
    image = convert.flatAsImage(data)
    return _save(file, image)


def _savegif(file, data):
    image3D = convert.to3D(data)
    path.safeMkdirsForFile(file)
    imageio.mimsave(file, image3D)
    return file


def save(file, data, flag=None):
    mapping = {None: _save, "flat": _saveflat, "animated": _savegif}
    func = mapping.get(flag)
    if not func:
        raise Exception("Unknow flag: {}".format(flag))
    return func(file, data)


def saves(filepathPrefix, images, workers=None):
    counts = len(images)
    n = len(str(counts))
    workers = workers or min(counts, asyncio.WORKERS)
    with asyncio.multiThread(workers) as pool:
        for index, image in enumerate(images):
            pool.apply_async(
                _save,
                args=("{}_{}.png".format(filepathPrefix, str(index).zfill(n)), image),
            )
    return filepathPrefix


def saveall(filepathPrefix, data, workers=None, pool=None):
    def _save(filepathPrefix, image3D, pool):
        layers = len(image3D)
        n = len(str(layers))
        for index, image in enumerate(image3D):
            pool.apply_async(
                _save,
                args=("{}_{}.png".format(filepathPrefix, str(index).zfill(n)), image),
            )
        pool.apply_async(_saveflat, args=("{}.png".format(filepathPrefix), image3D))
        pool.apply_async(_savegif, args=("{}.gif".format(filepathPrefix), image3D))

    image3D = convert.to3D(data)
    if pool:
        _save(filepathPrefix, image3D, pool)
    else:
        layers = len(image3D)
        workers = workers or min(layers + 2, asyncio.WORKERS)
        with asyncio.multiThread(workers) as _pool:
            _save(filepathPrefix, image3D, _pool)
    return filepathPrefix
