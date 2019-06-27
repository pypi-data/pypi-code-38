# -*- coding: utf-8 -*-
#
# This file is part of ProjectBubble.
#
# (c) Giant - MouGuangyi <mouguangyi@ztgame.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#


# 任务
class Task:
    def __init__(self, steps):
        def decorator():
            steps()
            return

        decorator()


task = Task
