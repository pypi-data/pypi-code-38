import cProfile
import time
import traceback


def conn_try_again(function):
    retries = 5
    # retry time
    count = {"num": retries}

    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as err:
            if count['num'] < 2:
                count['num'] += 1
                return wrapped(*args, **kwargs)
            else:
                raise Exception(err)

    return wrapped


def catch_exception(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as err:
            traceback.print_exc()

    return wrapped


def exeTime(function):
    def wrapped(*args, **kwargs):
        t0 = time.time()
        print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), function.__name__))
        back = function(*args, **kwargs)
        print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), function.__name__))
        print("@%.3fs taken for {%s}" % (time.time() - t0, function.__name__))
        return back

    return wrapped


def statsProfile(function):
    """
    statics the detail of method run
    :param function:
    :return:
    """

    def wrapped(*args, **kwargs):
        profile = cProfile.Profile()
        profile.enable()
        back = function(*args, **kwargs)
        profile.disable()
        profile.print_stats(sort="tottime")

        return back

    return wrapped
