# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/12
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.mbridge import motion_navigate_bridge
from bayeslibs.config import const, setting


class ApolloNAVer:
    """
    自动导航模块封装类，包括开始，结束，查询运动状态
    """

    def __init__(self):
        pass

    @staticmethod
    def start(destination):
        return start_auto_nav(destination)

    @staticmethod
    def stop():
        return stop_auto_nav()

    @staticmethod
    def status():
        return get_auto_nav_status()


def start_auto_nav(destination):
    """
    控制机器人导航到指定地点
    :param destination:
    :return:result
    :example:
        '''导航至destination'''
        result = start_auto_nav(destination)
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    if destination in setting.ROOM_MAP:
        x = setting.ROOM_MAP[destination][0]
        y = setting.ROOM_MAP[destination][1]
        print('发送自动导航指令:导航至{}'.format(destination))
        data = {
            'x': x,
            'y': y,
            'theta': 0
        }
        result = motion_navigate_bridge(req_type=const.TYPE_START, data=data)
    else:
        result = {
            'status': 404,
            'msg': '{} not in map'.format(destination)
        }
    return result


def stop_auto_nav():
    """
    停止机器人的导航
    :return:result
    :example:
        result = stop_auto_nav()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送停止自动导航指令}')
    result = motion_navigate_bridge(req_type=const.TYPE_STOP)
    return result


def get_auto_nav_status():
    """
    查询机器人导航状态
    :return:result
    :example:
        ret, msg = get_auto_nav_status()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('查询自动导航状态')
    result = motion_navigate_bridge(req_type=const.TYPE_QUERY)
    return result
