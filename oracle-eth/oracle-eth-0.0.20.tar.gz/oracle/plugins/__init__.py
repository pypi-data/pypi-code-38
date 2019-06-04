#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-17 12:37:21
LastEditors:  
LastEditTime: 2019-04-17 12:37:21
Description:  
"""
from oracle.logger import logger
import toolz

class Processor(object):
    # 注册的组件
    """
    PLUGINS = {
        'event_handle': {
            'DIDAttributeChange': CLASS,    // 处理指定`event`的class
            'DIDAttributeConfirmed': CLASS
        },
        'identity': {
            'DIDAttributeChange': {
                '士兵': 'Class',    // 不同的身份不同的处理函数
                'soldier': 'Class'
            },
            'DIDAttributeConfirmed': {
                '士兵': 'Class',
                'soldier': 'Class'
            }
        }
    }
    """
    PLUGINS = {}

    def process_identity(self, event, identity, entry):
        if identity not in toolz.get_in(['identity', event], self.PLUGINS):
            logger.error("{} 这个插件不存在, 请检查代码".format(identity))
        else:
            if hasattr(self.PLUGINS['identity'][event][identity], 'before'):
                self.PLUGINS['identity'][event][identity]().before(entry)

            self.PLUGINS['identity'][event][identity]().process(entry)

            if hasattr(self.PLUGINS['identity'][event][identity], 'after'):
                self.PLUGINS['identity'][event][identity]().after(entry)

    def process_event(self, event, entry):
        if 'event_handle' not in self.PLUGINS:
            logger.error("系统目前没有任何`event`插件, 请检查代码".format(event))
        else:
            if event not in self.PLUGINS['event_handle']:
                logger.error("{} 这个插件不存在, 请检查代码".format(event))
            else:
                if hasattr(self.PLUGINS['event_handle'][event], 'before'):
                    self.PLUGINS['event_handle'][event]().before(entry)

                self.PLUGINS['event_handle'][event]().process(entry)

                if hasattr(self.PLUGINS['event_handle'][event], 'after'):
                    self.PLUGINS['event_handle'][event]().after(entry)

        pass

    @classmethod
    def plugin_register(cls, event=None, identitys=[]):
        """
        注册插件的包装器
        如果`identitys`没有数据，注册的就是对应`event`事件的插件，用于处理对应的event的数据
        如果`identitys`有数据，注册的就是`event`中具体身份的处理函数
        :param event:
        :param identitys:
        :return:
        """
        if event is None:
            print('注册的event不能为空')
            exit(2)
        def wrapper(plugin):
            if len(identitys) == 0:
                if 'event_handle' not in cls.PLUGINS:
                    cls.PLUGINS.update({'event_handle': {event: plugin}})
                else:
                    cls.PLUGINS['event_handle'].update({event: plugin})
            for identity in identitys:
                if 'identity' not in cls.PLUGINS:
                    cls.PLUGINS.update({'identity': {event: {identity: plugin}}})
                else:
                    cls.PLUGINS = toolz.assoc_in(cls.PLUGINS, ['identity', event, identity], plugin)
            return plugin
        return wrapper
