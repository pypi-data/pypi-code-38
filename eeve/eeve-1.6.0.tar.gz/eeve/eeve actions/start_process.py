import subprocess


def run(*args, windowed=False, **kwargs):
    if windowed:
        kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE
    print('start process:', args, kwargs)
    subprocess.Popen(args, **kwargs)


actions = {'start process': {'run': run}}
