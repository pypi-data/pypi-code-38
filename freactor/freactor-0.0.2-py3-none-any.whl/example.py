import logging
from random import random
from time import sleep

from freactor import Freactor, StatusCode, freactor_reducer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

SUCCESS = StatusCode.SUCCESS
FAILURE = StatusCode.FAILURE
RETRY = StatusCode.RETRY
ABORT = StatusCode.ABORT

TASK_CONFIG = {
    'example_task_1': {
        'init_step': ('example', 's1'),
        'table': {
            ('example', 's1'): {
                SUCCESS: ('example', 's3'),
                FAILURE: None,
                RETRY: ('example', 's1'),
                ABORT: None,
            },
            ('example', 's2'): {
                SUCCESS: None,
                FAILURE: None,
                RETRY: ('example', 's2'),
                ABORT: None,
            },
            ('example', 's3'): {
                SUCCESS: ('example', 's5'),
                FAILURE: ('example', 's2'),
                RETRY: ('example', 's3'),
                ABORT: None,
            },
            ('example', 's4'): {
                SUCCESS: ('example', 's2'),
                FAILURE: None,
                RETRY: ('example', 's4'),
                ABORT: None,
            },
            ('example', 's5'): {
                SUCCESS: None,
                FAILURE: ('example', 's4'),
                RETRY: ('example', 's5'),
                ABORT: None,
            }
        }
    }
}


# s1, s2, s3... function demonstrate simple cleanup-based workflow
@freactor_reducer(3, 1)
def s1(t_data):
    log.info('s1 running...')
    log.info(t_data)
    sleep(1)
    r = random()
    if r < 0.9:
        return StatusCode.SUCCESS, {'s1': 1}, 's1 general success'
    else:
        return StatusCode.ABORT, {'s1': 1}, 's1 fail, abort'


@freactor_reducer()
def s2(t_data): # cleanup step of s1
    log.info('s2 running...')
    log.info(t_data)
    sleep(1)
    r = random()
    if r < 0.9:
        return StatusCode.SUCCESS, {'s2': 2}, 's2 general success'
    else:
        raise Exception('Woo! s2 raised!')


@freactor_reducer(3, 1)
def s3(t_data):
    log.info('s3 running...')
    log.info(t_data)
    sleep(1)
    r = random()
    if r < 0.3:
        return StatusCode.SUCCESS, {'s3': 1}, 's3 general success'
    else:
        raise Exception('Woo! s3 raised!')


@freactor_reducer()
def s4(t_data): # cleanup step of s3
    log.info('s4 running...')
    log.info(t_data)
    sleep(1)
    r = random()
    if r < 0.9:
        return StatusCode.SUCCESS, {'s4': 4}, 's4 general success'
    else:
        raise Exception('Woo! s4 raised!')


@freactor_reducer()
def s5(t_data):
    log.info('s5 running...')
    log.info(t_data)
    sleep(1)
    r = random()
    if r < 0.2:
        return StatusCode.SUCCESS, {'s5': 5}, 's5 general success'
    else:
        raise Exception('Woo! s5 raised!')


def main():
    print('Hello')
    log.debug('Hello')
    f = Freactor({
        'task_config': TASK_CONFIG,
        'threads': 4,
    })

    f.run_task('example_task_1', {})

    while True: pass

if __name__ == '__main__':
    main()
