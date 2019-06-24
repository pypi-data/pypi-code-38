# -*- coding: utf-8 -*-

from plone.indexer import indexer
from ideabox.policy.content.project import IProject

import hashlib


@indexer(IProject)
def project_picture(obj):
    images = obj.listFolderContents(contentFilter={"portal_type": "Image"})
    if images:
        obj.image = images[0].image
        return images[0].id


def random_hash(obj, method, r_min=0, r_max=32):
    me = getattr(hashlib, method)
    return me(obj.id).hexdigest()[r_min:r_max]


@indexer(IProject)
def project_random_1(obj):
    return random_hash(obj, 'md5', r_min=0, r_max=32)


@indexer(IProject)
def project_random_2(obj):
    return random_hash(obj, 'sha256', r_min=0, r_max=32)


@indexer(IProject)
def project_random_3(obj):
    return random_hash(obj, 'sha256', r_min=32, r_max=64)


@indexer(IProject)
def project_random_4(obj):
    return random_hash(obj, 'sha512', r_min=0, r_max=32)


@indexer(IProject)
def project_random_5(obj):
    return random_hash(obj, 'sha512', r_min=32, r_max=64)


@indexer(IProject)
def project_random_6(obj):
    return random_hash(obj, 'sha512', r_min=64, r_max=96)


@indexer(IProject)
def project_random_7(obj):
    return random_hash(obj, 'sha512', r_min=96, r_max=128)
