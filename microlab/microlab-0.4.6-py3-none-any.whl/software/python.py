import platform


def statistics():
    return {
            'version': platform._sys_version()[1],
            }
