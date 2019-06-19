import psutil


def statistics():
    return {'percent': psutil.virtual_memory().percent,
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'free': psutil.virtual_memory().free,
            'used': psutil.virtual_memory().used,
            }
