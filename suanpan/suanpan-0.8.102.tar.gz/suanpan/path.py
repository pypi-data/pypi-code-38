# coding=utf-8
from __future__ import absolute_import, print_function

import base64
import hashlib
import itertools
import os
import shutil

from suanpan import asyncio


def safeMkdirs(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
    return path


def safeMkdirsForFile(filepath):
    return safeMkdirs(os.path.dirname(os.path.abspath(filepath)))


def mkdirs(path, parent=False):
    mkdirFunction = safeMkdirsForFile if parent else safeMkdirs
    return mkdirFunction(path)


def merge(paths, dist, mode="move"):
    safeMkdirs(dist)
    mergeFunc = getattr(shutil, mode)
    for path in paths:
        if os.path.isfile(path):
            mergeFunc(path, dist)
        else:
            for p in os.listdir(path):
                subpath = os.path.join(path, p)
                mergeFunc(subpath, dist)
            if mode == "move":
                os.rmdir(path)
    return dist


def md5(filepath, block_size=64 * 1024):
    with open(filepath, "rb") as f:
        _md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            _md5.update(data)
    return base64.b64encode(_md5.digest()).decode()


def empty(folder):
    def _safeListDir(folder):
        try:
            return os.listdir(folder)
        except OSError:
            return []

    for path in _safeListDir(folder):
        remove(os.path.join(folder, path))
    return folder


def remove(path):
    removeFunction = removeFile if os.path.isfile(path) else removeFolder
    return removeFunction(path)


def removeFile(filePath):
    if os.path.exists(filePath):
        try:
            os.remove(filePath)
        except (FileNotFoundError, OSError):
            pass
    return filePath


def removeFolder(folderPath):
    if os.path.exists(folderPath):
        try:
            shutil.rmtree(folderPath)
        except (FileNotFoundError, OSError):
            pass
    return folderPath


def removeEmptyFolders(folderPath):
    try:
        os.removedirs(folderPath)
    except OSError:
        pass
    return folderPath


def copy(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    copyFunction = copyFile if os.path.isfile(src) else copyFolder
    return copyFunction(src, dst)


def copyFile(src, dst):
    mkdirs(dst, parent=True)
    shutil.copyfile(src, dst)
    return dst


def copyFolder(src, dst):
    remove(dst)
    mkdirs(dst, parent=True)
    shutil.copytree(src, dst)
    return dst


def getPathDepth(root, path):
    root = root.rstrip(os.sep)
    path = path.rstrip(os.sep)
    return path[len(root) :].count(os.sep)


def listdir(path, depth=1):
    folders, files = zip(
        *[
            (
                [os.path.join(root, folder) for folder in folders],
                [os.path.join(root, file) for file in files],
            )
            for root, folders, files in os.walk(path)
            if depth is True or getPathDepth(path, root) < depth
        ]
    )
    return list(itertools.chain(*folders)), list(itertools.chain(*files))


def replaceBasePath(src, dst, *paths):
    src = src.rstrip(os.sep)
    dst = dst.rstrip(os.sep)
    return [path.rstrip(os.sep).replace(src, dst) for path in paths]


# Concurrent Funcs


def cremove(path, workers=None):
    removeFunction = cremoveFile if os.path.isfile(path) else cremoveFolder
    return removeFunction(path, workers=workers)


def cremoveFile(filePath, workers=None):  # pylint: disable=unused-argument
    return removeFile(filePath)


def cremoveFolder(folderPath, workers=None):
    cempty(folderPath, workers=workers)
    return remove(folderPath)


def cempty(folderPath, workers=None):
    folders, files = listdir(folderPath, depth=True)
    asyncio.map(remove, files, pbar="Removing Files", workers=workers)
    asyncio.map(remove, folders, pbar="Removing Folders", workers=workers)
    return folderPath


def ccopy(src, dst, workers=None):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    copyFunction = ccopyFile if os.path.isfile(src) else ccopyFolder
    return copyFunction(src, dst, workers=workers)


def ccopyFile(src, dst, workers=None):  # pylint: disable=unused-argument
    return copyFile(src, dst)


def ccopyFolder(src, dst, workers=None):
    folders, files = listdir(src, depth=True)
    newfolders = replaceBasePath(src, dst, *folders)
    newfiles = replaceBasePath(src, dst, *files)
    mkdirs(dst)
    asyncio.map(mkdirs, newfolders, pbar="Making Folders", workers=workers)
    asyncio.starmap(copy, zip(files, newfiles), pbar="Copying Files", workers=workers)
    return dst
