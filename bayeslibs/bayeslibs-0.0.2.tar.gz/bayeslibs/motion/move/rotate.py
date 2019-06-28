# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.mbridge import motion_rotate_bridge
from bayeslibs.config import const
from cmath import pi


class ApolloRotator:
    def __init__(self):
        pass

    @staticmethod
    def get_rotate_status():
        rotate_stat = get_robot_rotate_status()
        while rotate_stat and rotate_stat['status'] != 0:
            rotate_stat = get_robot_rotate_status()
        return True

    def turn_right(self):
        robot_turn_right()
        self.get_rotate_status()
        return True

    def turn_left(self):
        robot_turn_left()
        self.get_rotate_status()
        return True

    def rotate_right(self, angle):
        robot_rotate_right(angle)
        self.get_rotate_status()
        return True

    def rotate_left(self, angle):
        robot_rotate_left(angle)
        self.get_rotate_status()
        return True

    @staticmethod
    def stop_rotate():
        return stop_robot_rotate()


def robot_rotate_left(angle):
    """
    控制机器人向左转动特定角度
    :param angle:转动角度
    :return:result
    :example:
        '''向左转动30度'''
        result = robot_rotate_left(30)
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送向左转动指令:{}度'.format(angle))
    data = {
        'x': 0,
        'y': 0,
        'theta': angle / 180 * pi
    }
    result = motion_rotate_bridge(req_type=const.TYPE_START, data=data)
    return result


def robot_rotate_right(angle):
    """
    控制机器人向右转动特定角度
    :param angle:转动角度
    :return:result
    :example:
        '''向右转动30度'''
        result = robot_rotate_right(30)
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送向右转动指令:{}度'.format(angle))
    data = {
        'x': 0,
        'y': 0,
        'theta': -angle / 180 * pi
    }
    result = motion_rotate_bridge(req_type=const.TYPE_START, data=data)
    return result


def robot_rotate_back():
    """
    控制机器人向后转动
    :param
    :return:result
    :example:
        '''向后转动'''
        result = robot_rotate_back()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送向后转动指令')
    data = {
        'x': 0,
        'y': 0,
        'theta': pi
    }
    result = motion_rotate_bridge(req_type=const.TYPE_START, data=data)
    return result


def robot_turn_left():
    """
    控制机器人向左转动90度
    :param
    :return:result
    :example:
        '''向后转动'''
        result = robot_turn_left()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送向左转动90度指令')
    data = {
        'x': 0,
        'y': 0,
        'theta': 0.5 * pi
    }
    result = motion_rotate_bridge(req_type=const.TYPE_START, data=data)
    return result


def robot_turn_right():
    """
    控制机器人向右转动90度
    :param
    :return:result
    :example:
        '''向后转动'''
        result = robot_turn_right()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送向右转动90度指令')
    data = {
        'x': 0,
        'y': 0,
        'theta': -0.5 * pi
    }
    result = motion_rotate_bridge(req_type=const.TYPE_START, data=data)
    return result


def stop_robot_rotate():
    """
    停止机器人的转动
    :return:result
    :example:
        result = stop_robot_rotate()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('发送停止转动指令}')
    result = motion_rotate_bridge(req_type=const.TYPE_STOP)
    return result


def get_robot_rotate_status():
    """
    查询机器人转动状态
    :return:result
    :example:
        ret, msg = get_robot_rotate_status()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = motion_rotate_bridge(req_type=const.TYPE_QUERY)
    print('查询转动状态:{}'.format(result))
    return result


if __name__ == '__main__':
    print(pi)
