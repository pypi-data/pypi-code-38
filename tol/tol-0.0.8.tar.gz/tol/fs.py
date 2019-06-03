def mkdir(path, mode=None):
    return 'mkdir --parents {mode} {path}'.format(
        path=path,
        mode='--mode %s' % mode if mode else '')


def chown(user, path):
    return 'chown --recursive %s:%s %s' % (user, user, path)


def exists(path):
    return "test -e %s" % path
