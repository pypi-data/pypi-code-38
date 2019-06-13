import sys

def usage(return_code):
    s = (
        "Usage:\n"
        "coolsignup --version\n"
        "coolsignup serve -c <conf> -p <port>\n"
    )
    if return_code == 0:
        sys.stdout.write(s)
        sys.stdout.flush()
    else:
        sys.stderr.write(s)
        sys.stderr.flush()
    sys.exit(return_code)


def get_command():
    try:
        return sys.argv[1]
    except IndexError:
        usage(1)

def get_option(prefix):
    try:
        c_index = next(
            i
            for i, arg in enumerate(sys.argv)
            if arg == prefix
        )
        return sys.argv[c_index + 1]
    except (StopIteration, IndexError):
        usage(1)
