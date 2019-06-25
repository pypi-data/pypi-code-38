from feedgen.feed import FeedGenerator

from podenco.domain.podcast import Podcast


class PodcastEnconderRSS:
    @staticmethod
    def serialize(podcast: Podcast, pretty: bool = False) -> str:
        fg = FeedGenerator()
        fg.load_extension("podcast")
        # fg.podcast.itunes_author(podcast.author.name)
        # fg.podcast.itunes_category("Technology", "Podcasting")
        # fg.podcast.itunes_explicit("no")
        # fg.podcast.itunes_complete("no")
        # fg.podcast.itunes_new_feed_url("http://example.com/new-feed.rss")
        # fg.podcast.itunes_owner("John Doe", "john@doe.com")
        # fg.podcast.itunes_summary("")
        fg.title(podcast.title)
        fg.description(podcast.description)
        fg.author(podcast.author.to_dict())
        fg.link(href=podcast.atom_url, rel="self")
        fg.logo(podcast.logo_url)

        for episode in podcast.episodes:
            fe = fg.add_entry()
            fe.id(podcast.episode_audio_url(episode))
            fe.title(episode.title)
            fe.description(episode.description)
            fe.enclosure(podcast.episode_audio_url(episode), 0, "audio/mpeg")
            # fe.author(**podcast.author.to_dict())
            # fe.podcast.itunes_author(podcast.author.name)

        return fg.rss_str(pretty=pretty).decode("utf-8")
