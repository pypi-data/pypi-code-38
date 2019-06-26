from subprocess import call


def cls():
    try:
        call('clear', shell=True)
    except OSError:
        call('cls')
    except Exception as e:
        print(type(e).__name__, e)


if __name__ == "__main__":
    cls()
