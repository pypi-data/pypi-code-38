from os.path import join, expanduser


class PathTools(object):
    @classmethod
    def get_home_path(cls):
        return expanduser("~")

    @classmethod
    def get_ssh_path(cls):
        return join(cls.get_home_path(), '.ssh', 'id_rsa')
