from subprocess import call


def clear():
    try:
        call('clear', shell=True)
    except OSError:
        call('cls', shell=True)
    except Exception as e:
        print(type(e).__name__, e)
