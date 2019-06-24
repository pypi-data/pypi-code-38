# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.discussion.browser.comments import CommentsViewlet as BaseViewlet
from plone.app.discussion.browser.comments import CommentForm as BaseForm

import six


class CommentForm(BaseForm):
    def get_author(self, data):
        context = aq_inner(self.context)
        # some attributes are not always set
        author_name = u""

        # Make sure author_name/ author_email is properly encoded
        if "author_name" in data:
            author_name = data["author_name"]
            if isinstance(author_name, str):
                author_name = six.text_type(author_name, "utf-8")
        if "author_email" in data:
            author_email = data["author_email"]
            if isinstance(author_email, str):
                author_email = six.text_type(author_email, "utf-8")

        # Set comment author properties for anonymous users or members
        portal_membership = getToolByName(context, "portal_membership")
        anon = portal_membership.isAnonymousUser()
        if not anon and getSecurityManager().checkPermission("Reply to item", context):
            # Member
            member = portal_membership.getAuthenticatedMember()
            # memberdata is stored as utf-8 encoded strings
            email = member.getProperty("email")
            infos = [member.getProperty("first_name"), member.getProperty("last_name")]
            fullname = " ".join([i for i in infos if i])
            if not fullname or fullname == "":
                fullname = member.getUserName()
            elif isinstance(fullname, str):
                fullname = six.text_type(fullname, "utf-8")
            author_name = fullname
            if email and isinstance(email, str):
                email = six.text_type(email, "utf-8")
            # XXX: according to IComment interface author_email must not be  # noqa T000
            # set for logged in users, cite:
            # 'for anonymous comments only, set to None for logged in comments'
            author_email = email
            # /XXX  # noqa T000

        return author_name, author_email


class CommentsViewlet(BaseViewlet):
    form = CommentForm

    def get_commenter_home_url(self, username=None):
        return
