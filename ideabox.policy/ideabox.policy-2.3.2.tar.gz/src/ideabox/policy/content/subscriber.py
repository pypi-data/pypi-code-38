# -*- coding: utf-8 -*-

from ideabox.policy.content.project import IProject
from plone.protect.auto import safeWrite
from zope.globalrequest import getRequest


def project_image_changed(obj, event):
    if hasattr(obj, "aq_parent") is False:
        return
    if IProject.providedBy(obj.aq_parent):
        obj.aq_parent.reindexObject(idxs=["project_picture"])


def project_added(obj, event):
    request = getRequest()
    safeWrite(obj, request)
    obj.allow_discussion = True
