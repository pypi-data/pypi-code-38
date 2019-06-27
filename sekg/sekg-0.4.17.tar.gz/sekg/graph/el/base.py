import abc


class EntityLinkResult:
    def __init__(self, mention, node_id, node_name=None, score=1.0, **extra_info):
        self.mention = mention
        self.node_id = node_id
        self.node_name = node_name
        self.score = score

        self.extra_info = extra_info

    def __repr__(self):
        return "<EntityLinkResult mention=%r id=%r name=%r score=%r>" % (
            self.mention, self.node_id, self.node_name, self.score)


class EntryPointLinker:
    @abc.abstractmethod
    def link(self, query, **config):
        pass
