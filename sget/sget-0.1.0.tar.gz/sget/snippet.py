class Snippet():
    def __init__(self, content, description, name, groups=None):
        self._content = content
        self._description = description
        self._name = name
        if not groups:
            groups = []
        self._groups = groups

    @property
    def content(self):
        return self._content

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name

    @property
    def groups(self):
        return self._groups

    def to_dict(self):
        return {'content': self.content,
                'description': self.description,
                'groups': self.groups}

    def __repr__(self):
        msg = 'Snippet:\ncontent - {}\ndescription - {}'
        return msg.format(self._content, self._description)

    def __eq__(self, other):
        return (isinstance(other, Snippet)
                and self.name == other.name
                and self.content == other.content
                and self.description == other.description
                and self.groups == other.groups)

    @staticmethod
    def from_dict(data, name):
        content = data['content']
        description = data['description']
        groups = data.get('groups')
        return Snippet(content=content,
                       description=description,
                       name=name,
                       groups=groups)

    @staticmethod
    def is_template(content):
        return '<$>' in content


class SnippetCollection():
    def __init__(self, snippets=None):
        self._lookup = {}
        self._groups = {}
        if snippets:
            for snippet in snippets:
                self.add(snippet)

    def __iter__(self):
        for name, snippet in self._lookup.items():
            yield Snippet.from_dict(snippet, name)

    def __len__(self):
        return len(self._lookup)

    def groups(self):
        return list(self._groups.keys())

    def get_group(self, group):
        collection = SnippetCollection()
        for name in self._groups[group]:
            collection.add(self.get(name))
        return collection

    def get(self, name):
        return Snippet.from_dict(self._lookup[name], name)

    def add(self, snippet, overwrite=False):
        name = snippet.name
        if self._lookup.get(name) is not None and not overwrite:
            msg = 'Snippet with name {} already exists'
            raise ValueError(msg.format(name))
        self._lookup[name] = snippet.to_dict()
        for group in snippet.groups:
            collection_group = self._groups.setdefault(group, set())
            collection_group.add(snippet.name)

    def rm(self, name):
        snippet = self.get(name)
        for group in snippet.groups:
            try:
                self._groups[group].remove(snippet.name)
            except KeyError:
                pass
        del self._lookup[name]

    def exists(self, name):
        return self._lookup.get(name) is not None

    def to_dict(self):
        return self._lookup

    @staticmethod
    def from_dict(snippet_dict):
        collection = SnippetCollection()
        for name, snippet in snippet_dict.items():
            collection.add(Snippet.from_dict(snippet, name))
        return collection
