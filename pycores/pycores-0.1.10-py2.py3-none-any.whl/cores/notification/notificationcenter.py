#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict

class NotificationCenter(object):
    _listeners = None

    def __new__(type):
        if not '_singleton' in type.__dict__:
            type._singleton = object.__new__(type)
            type._singleton._listeners = defaultdict(list)

        return type._singleton

    def on(self, etype, listener):
        self._listeners[etype].append(listener)

    def off(self, etype, listener=None):
        # self._listeners.remove(etype)
        pass

    def fire(self, notification):
        # 前置
        preEvent = notification.pre()
        if preEvent:
            for l in self._listeners[preEvent.type()]:
                if l(notification): # 如果返回 True ，那么消息不再传递下去
                    break;

        for l in self._listeners[notification.type()]:
            if l(notification): # 如果返回 True ，那么消息不再传递下去
                break;


        # 后置
        postEvent = notification.post()
        if postEvent:
            for l in self._listeners[postEvent.type()]:
                if l(notification): # 如果返回 True ，那么消息不再传递下去
                    break;