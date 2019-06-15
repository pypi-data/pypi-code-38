from threading import Thread


class Tree:
    def __init__(self, repository, children):
        self.repository = repository
        self.children = children

    def execute(self, command, concurrent=False):
        if self.repository is not None:
            if concurrent:
                Thread(target=command, args=(self.repository,)).start()
            else:
                command(self.repository)

        for child in self.children:
            child.execute(command, concurrent=concurrent)


class Repository:
    def __init__(self, path, url, kind="git"):
        self.path = path
        self.url = url
        self.kind = kind
