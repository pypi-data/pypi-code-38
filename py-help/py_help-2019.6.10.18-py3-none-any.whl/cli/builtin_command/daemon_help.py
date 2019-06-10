# -*- coding: utf-8 -*-
import os
import time
from py_help.api_help.api_wrapper import Api
from .. import debug, info, warn, error

DAEMON_SET_FILE = '/sf/log/vst_daemon.set'

@Api()
def set_daemon(**kwargs):
    """
    @api /py/daemon_run
    @name daemon模式
    @toolable
    @description 启动了daemon模式之后,后续的命令都是daemon模式运行,daemon模式运行执行速度会快很多(少了文件加载的动作)
    @author 王沃伦
    @params
        stop,name:关闭,type:s,required:false,default:否,desc:默认可以不设置这个,不设置就是启动daemon模式,设置了是就是关闭daemon模式
    @example
        usage:set daemon_run --stop,desc:关闭daemon运行
        usage:set daemon_run,desc:启动daemon运行
    @expect 成功|失败|NONE
    """
    is_stop = kwargs.get('stop', False)
    info('是否停止daemon::{stop}'.format(stop=is_stop))
    if is_stop and os.path.exists(DAEMON_SET_FILE):
        os.remove(DAEMON_SET_FILE)
    else:
        set_file = open(DAEMON_SET_FILE, 'w')
        set_file.write('{time}{pid}'.format(time=time.time(), pid=os.getpid()))
        set_file.flush()
        set_file.close()
    return {'exit': 0, 'out': 'success'}
