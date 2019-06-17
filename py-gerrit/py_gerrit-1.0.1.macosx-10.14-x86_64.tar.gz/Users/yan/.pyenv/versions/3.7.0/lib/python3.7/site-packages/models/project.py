# -*- coding: utf-8 -*-
# @Time    : 19-5-21 下午5:04
# @Author  : allen.you

from utils.jsonModel import jsonModel


@jsonModel()
class Weblink(object):
    def __init__(self):
        self.name = ''
        self.url = ''
#
# @jsonModel()
# class Value(object):
#     def __init__(self):
#         self.' 0' = "No score"
#         self."-1" = "I would prefer this is not merged as is"
#         self."-2" = "This shall not be merged"
#         self."+1" = "Looks good to me, but someone else must approve"
#         self.'+2' = "Looks good to me, approved"
#
# @jsonModel(objectMap={'values': Value})
# class CodeReview(object):
#     def __init__(self):
#         self.values = {}
#
#
# @jsonModel(objectMap={'Code-Review': CodeReview})
# class Label(object):
#     def __init__(self):
#         self.Code_Review = {}
#         self.default_value = 0


@jsonModel(listClassMap={'web_links': Weblink})
class Project(object):

    def __init__(self):
        self.id = ''
        self.name = ''
        self.parent = ''
        self.state = ''
        self.web_links = []
        self.labels = ''


    def __repr__(self):
        return 'Project Name: %s, State: %s' % (self.id, self.state)