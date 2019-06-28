# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/12
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.mbridge import motion_map_bridge
from bayeslibs.config import const


class ApolloMapSaver:
    """
    转动运动模块封装类，包括向前、向后运动特定距离，停止转动，查询运动状态
    """

    def __init__(self, type_):
        self.type = type_

    def rotate(self, angle):
        return motion_map_bridge(req_type=self.type, data=angle)

    def stop(self):
        return motion_map_bridge(req_type=self.type)

    def status(self):
        return motion_map_bridge(req_type=self.type)


def robot_map_save(map_name):
    """
    控制机器人向后运动特定距离
    :param map_name:转动角度
    :return:result
    :example:
        '''向后运动3m'''
        result = robot_move_back(3)
        print('result:', result)
        ------
        result:True
    """
    print('发送向后运动指令:{}m'.format(map_name))
    result = motion_map_bridge(req_type=const.TYPE_START, data=map_name)
    return result
