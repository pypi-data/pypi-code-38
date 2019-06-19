
class BlogException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message


class PathError(BlogException):
    def __init__(self, path, *args):
        super().__init__("Path error: {}".format(path), *args)


class AuthorizationError(BlogException):
    def __init__(self, content):
        super().__init__("Accès interdit au contenu: {} ({})".format(content.title, content.url))
