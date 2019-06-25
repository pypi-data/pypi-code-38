import typing
import attr


@attr.s(auto_attribs=True)
class Author:
    name: str
    email: str

    def to_dict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True)
class Episode:
    id: int
    title: str
    description: str
    audio_file: str


@attr.s(auto_attribs=True)
class Podcast:
    title: str
    subtitle: str
    description: str
    author: Author
    base_url: str
    episodes: typing.List[Episode] = attr.Factory(list)

    @property
    def atom_url(self) -> str:
        return self.base_url + "/podcast.atom"

    @property
    def rss_url(self) -> str:
        return self.base_url + "/podcast.rss"

    @property
    def logo_url(self) -> str:
        return self.base_url + "/podcast.jpg"

    def episode_audio_url(self, episode: Episode) -> str:
        return "{}/{}/audio.mp3".format(self.base_url, episode.id)
