# -*- coding: utf-8 -*-
# @Time    : 2018/4/1 下午9:47
#  @File    : dubboapi.py
# @Software: PyCharm
import platform,sys
from commonpython import dubbotelnetpy3 as dubbo_telnet

import json,time


class DubboInterface(object):
    def __init__(self,host,port,timeout=10,**kwargs):
        """
        :param host:        dubbo服务器ip
        :param port:        端口
        :param timeout:     连接dubbo服务器的超时时间
        :param kwargs:
        """
        self.host=host
        self.port=port
        self.start_time=time.time()
        self.conn=dubbo_telnet.dubbo(self.host, self.port)
        self.conn.set_connect_timeout(timeout)


    def dubbo_call(self,interface,method,param,is_param=1):  #调用函数
        """
        :param interface:   dubbo接口服务
        :param method:      调用方法
        :param param:       调用dubbo接口入参
        :param is_param:    是否需要参数转换   1:前端页面转换   0:不转化   2接口调用json转换
        :return:    返回调用结果
        """
        # 设置dubbo服务返回响应的编码
        try:
            if is_param == 1:
                res = json.loads(param) if type(param) == str else param
                param_str = ''
                for param_dict in res:
                    v = param_dict['var_data']
                    param_type = param_dict['var_type']
                    if isinstance(v, eval(param_type)):
                        v = '"{}"'.format(v)
                    elif isinstance(v, eval(param_type)):
                        v = str(v)
                    elif isinstance(v, eval(param_type)):
                        v = str(v)
                    else:
                        v = v
                    param_str = param_str + v + ','
                param_str=(param_str[:-1])
            elif is_param == 2:
                param_str = ''
                for data in param:
                    value = param[data]
                    if isinstance(value,int):
                        v = str(value)
                    else:
                        v = '"{}"'.format(value)
                    param_str = param_str + v + ','
                param_str = (param_str[:-1])
            else:
                param_str=param
        except:
            return json.dumps({"message":False,"data":"param_typeErr","response_time":0})
        else:
            self.conn.set_encoding('utf-8')   #python2中是gbk，默认返回编码也是gbk
            dubbo_res=self.conn.invoke(interface, method,param_str)
            end_time=time.time()
            call_time=round((end_time-self.start_time),3)
            if dubbo_res==None:
                return json.dumps({"message":False,"data":"telnet_error","response_time":0})  #连接dubbo服务失败
            return json.dumps({"response":dubbo_res,"response_time":call_time},ensure_ascii=False)     #返回dubbo调用结果,返回str类型

    def check_dubbo_result(self,dubbo_res,expect_result):
        """
        预期结果与实际结果比较
        :param dubbo_res:    dubbo接口调用结果
        :param expect_result:     dubbo接口预期结果
        :return:
        """

        if expect_result and expect_result != 'None':
            try:
                expect_result_list = expect_result.split(';')
            except Exception as e:
                return ['预期结果数据格式不正确，请使用;分割']
            else:
                fail_list = []
                for result in expect_result_list:
                    if result in dubbo_res:
                        continue
                    else:
                        fail_list.append(result)
                return fail_list
        else:
            return ['预期结果不存在，或者为None']




if __name__=='__main__':

    Host = '127.0.0.1'  # Doubble服务器IP
    Port = '20880'  # Doubble服务端口
    interface = 'com.alibaba.dubbo.demo.DemoService'
    method = 'getPermissions'
    # param = "[{\"var_name\":\"name\",\"var_data\":\"888\",\"var_type\":\"str\",\"var_remark\":\"\u59d3\u540d\"},{\"var_name\":\"id\",\"var_data\":\"1\",\"var_type\":\"int\",\"var_remark\":\"ID\"}]"        #如果dubbo接口入参是str类型,参数必须这样写
    param = {
        "name":"xulei",
        "id":1
    }
    test=DubboInterface(host=Host,port=Port,timeout=10)
    print(test.dubbo_call(interface=interface,method=method,param=param,is_param=2))




