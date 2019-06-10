from context import ezprogress
import time


def visual():
    """It makes little sense to do unittests of this module, so this will suffice."""
    pb = ezprogress.progressbar.ProgressBar(total=100, title='Progress', bar_length=50)
    pb.start()
    for i in range(0, 100):
        pb.update(i)
        time.sleep(0.01)
    pb.finished()


if __name__ == '__main__':
    visual()