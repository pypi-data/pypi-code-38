# -*- coding: utf-8 -*-
import weakref


class SDKLog(object):
    # instances = []
    #
    # def __init__(self):
    #     self.__class__.instances.append(weakref.proxy(self))
    #
    # def record_log(self, log):
    #     pass
    #
    # @staticmethod
    # def info(log):
    #     if(len(ISDKLog.instances)==0):
    #         return
    #     ISDKLog.instances[0].record_log(log)
    def info(self, log):
        print (log)

    def error(self, log):
        print (log)