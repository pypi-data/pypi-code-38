#!/usr/bin/env python


import time

class Timer():
    def __init__(self):
        self.stages = []

    def reset(self):
        self.stages = []
        

    def stage_begin(self, name):
        if self.stages:
            last = self.stages[-1]
            if len(last) < 3:
                last.append(time.time())

        new = [name, time.time()]
        self.stages.append(new)
        

    def stage_end(self, name):
        if self.stages:
            last = self.stages[-1]
            if len(last) < 3:
                last.append(time.time())

    def finish(self):
        if self.stages:
            last = self.stages[-1]
            if len(last) < 3:
                last.append(time.time())

    def dump(self):
        msg = ''
        
        total = 0.
        for stage in self.stages:
            dura = 1000 * (stage[2] - stage[1])
            name = stage[0]
            msg += str('[%s:%.1f]' % (name, dura))
            total += dura

        msg = 'total[%.1fms] ' % total + msg
        return msg

def main():
    _timer = Timer()
    _timer.stage_begin('stage1')
    time.sleep(0.5)
    _timer.stage_end('stage1')

    _timer.stage_begin('stage2')
    time.sleep(0.4)
    _timer.stage_begin('stage3')
    time.sleep(0.3)
    _timer.stage_begin('stage4')
    time.sleep(0.2)

    _timer.finish()

    print _timer.dump()


if __name__ == '__main__':
    main()
