# -*- coding: utf-8 -*-

from plone import api


def fix_comments_1001(context):
    from plone.app.discussion.interfaces import IConversation

    brains = api.content.find(
        context=api.portal.get(),
        total_comments={"query": [1, 1000], "range": "min:max"},
    )
    for brain in brains:
        obj = brain.getObject()
        conversation = IConversation(obj, None)
        for thread in conversation.getThreads():
            comment = thread["comment"]
            if comment.author_name == comment.author_email:
                user = api.user.get(username=comment.author_username)
                infos = [user.getProperty("first_name"), user.getProperty("last_name")]
                comment.author_name = " ".join([i for i in infos if i])
