# -*- coding: utf-8 -*-
import os
import time
from py_help.api_help.api_wrapper import Api
from .. import debug, info, warn, error

DAEMON_SET_FILE = '/sf/log/vst_daemon.set'


@Api()
def start_api_server(**kwargs):
    """
    @api /py/api_server
    @name API服务
    @toolable
    @description 启动了API服务后,可以通过api rpc来调度对应的命令或者是API
    @author 王沃伦
    @params
        server_type,name:服务类型,type:s,required:false,default:xml_rpc,desc:设置的服务类型
        ip,name:服务IP,type:s,required:false,default:0.0.0.0,desc:设置的服务地址
        port,name:服务端口,type:i,required:false,default:8080,desc:设置的服务端口
        url,name:服务url,type:s,required:false,default:/RPC2,desc:设置的服务url地址
    @example
        usage:py api_server --server_type=xml_rpc --port=8080 --url=/RPC2,desc:启动xml_rpc API服务,在端口8080,服务URL /RPC2
    @expect 成功|失败|NONE
    """
    from py_help.lib.xml_rpc_server import XmlRpcServer
    server_type = kwargs.get('server_type', 'xml_rpc')
    if server_type == 'xml_rpc':
        XmlRpcServer(kwargs.get('ip', '0.0.0.0'), kwargs.get('port', 8080), kwargs.get('url', '/RPC2')).start_server()
    elif server_type == 'json_rpc':
        warn("暂时不支持 json_rpc")
    elif server_type == 'grpc':
        warn("暂时不支持 grpc")
    return {'exit': 0, 'out': 'success'}
