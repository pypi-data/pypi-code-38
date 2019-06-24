class File:
    def __init__(self, content, filename=None):
        self.filename = filename or content.name
        self.content = content


class FileID:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.id


def remove_trailing_slash(path):
    if path and path[-1] == '/':
        path = path[:-1]
    return path


def make_timestamp(value):
    if value:
        value = value.isoformat()
    return value
