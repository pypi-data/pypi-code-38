import attr


@attr.s()
class PodcastLoad:
    repository = attr.ib()

    def execute(self):
        return self.repository.get()
