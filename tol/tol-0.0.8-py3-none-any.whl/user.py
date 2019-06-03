def exists(user):
    return 'getent passwd %s' % user


def add(user):
    return "useradd --create-home --shell /bin/bash %s" % user


def append_to_group(user, groups):
    return 'usermod --append --groups %s %s' % (",".join(groups), user)
