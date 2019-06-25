import attr
import yaml

from podenco.domain.podcast import Podcast, Author, Episode


@attr.s(auto_attribs=True)
class YamlRepository:
    yaml_str: str
    podcast: Podcast = attr.ib(init=False)

    def __attrs_post_init__(self):
        podcast_config = yaml.load(self.yaml_str, Loader=yaml.Loader)

        pc = podcast_config["podcast"]

        author = Author(name=pc["author"]["name"], email=pc["author"]["email"])

        episodes = []
        id_count = 1
        for episode in pc["episodes"]:
            episodes.append(Episode(id=id_count, **episode))
            id_count += 1

        self.podcast = Podcast(
            title=pc["title"],
            subtitle=pc["subtitle"],
            description=pc["description"],
            author=author,
            episodes=episodes,
            base_url=pc["base_url"],
        )

    def get(self):
        return self.podcast
