# -*- coding: utf-8 -*-

from enum import Enum
from .notification import Notification
from .notificationcenter import NotificationCenter

class NOTIFICATION(Enum):
    '''
    :brief 预定义事件类型
    '''

    # 吃饭
    EAT = 'eat'
    #睡觉
    SLEEP = 'sleep'

    AFTER_EAT = 'after eat'
    BEFORE_SLEEP = 'before sleep'

# print(type(EVENT.EAT.value))

NotificationEat = Notification(NOTIFICATION.EAT)
NotificationEatPost = Notification(NOTIFICATION.AFTER_EAT)
NotificationEat.before(NotificationEatPost)

NotificationSleep = Notification(NOTIFICATION.SLEEP)
NotificationSleepPre = Notification(NOTIFICATION.BEFORE_SLEEP)
NotificationSleep.after(NotificationSleepPre)

'''
'''

class sleep():
    def register(self):
        eventbus = NotificationCenter()

        eventbus.on(NotificationSleep.type(), self._on_sleep)
        eventbus.on(NotificationSleepPre.type(), self._pre_sleep)

    def _on_sleep(self, event):
        print('开始睡觉了')

    def _pre_sleep(self, event):
        print('睡觉之前')


class eat():
    def register(self):
        eventbus = NotificationCenter()

        eventbus.on(NotificationEat.type(), self._on_eat)
        eventbus.on(NotificationEatPost.type(), self._post_eat)

    def _on_eat(self, event):
        print('开始吃晚饭了')

    def _post_eat(self, event):
        print('饭吃好了，记得多走走')

def test():
    eventbus = NotificationCenter()

    eat().register()
    sleep().register()

    #启动事件驱动
    eventbus.fire(NotificationEat)
    eventbus.fire(NotificationSleep)

if __name__ == '__main__':
    test()