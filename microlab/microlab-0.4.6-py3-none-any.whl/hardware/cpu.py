import psutil
import multiprocessing
import platform


def statistics():
    return {
            'model': platform.processor(),
            'cores': multiprocessing.cpu_count(),
            'percent': psutil.cpu_percent(),
            }
