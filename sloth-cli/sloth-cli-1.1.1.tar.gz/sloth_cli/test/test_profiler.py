import time

from sloth_cli import profile


def _loop_sleep():
    """Loops and sleeps"""
    for i in range(3):
        print(i)
        time.sleep(1)


def _loop():
    """Loops 1000 times"""
    ints = []
    for i in range(1000):
        ints.append(i)


@profile(enable=True, lines=50, builtins=False)
def run():
    """Run loops"""
    _loop()
    _loop()
    _loop_sleep()


def test_profile():
    """"Should run without failures"""
    run()
