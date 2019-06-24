# -*- coding:utf-8 -*- 
__author__ = 'denishuang'


def extends_config(src_configs,dest_configs):
    return [ dest_configs.filter(name=config.name).first() or config for config in src_configs]
