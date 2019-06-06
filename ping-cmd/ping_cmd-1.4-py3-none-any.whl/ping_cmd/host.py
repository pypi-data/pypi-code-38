from subprocess import PIPE, Popen


def ping(host, packages=1, wait=2):
    """
    :param str host:
    :param int packages:
    :param int wait:
    :return int:
    """
    command = ['ping', '-n', str(packages), '-w', str(wait), host]
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"input data")
    return p.returncode