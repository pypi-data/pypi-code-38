import attr


@attr.s(slots=True)
class HardbackCursor:
    hardback = attr.ib()
    index = attr.ib(default=-1)

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index >= len(self.hardback.desc.sources):
            raise StopIteration
        return self

    @property
    def source(self):
        return self.hardback.desc.sources[self.index]

    @property
    def metadata(self):
        return self.hardback.metadatas[self.index]
