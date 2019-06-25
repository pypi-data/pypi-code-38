#!/usr/bin/env python

import unittest
import unittest.mock as mock

from feedgen.feed import FeedGenerator

from podenco.domain.podcast import Podcast, Author, Episode
from podenco.serializers import podcast_serializer_rss as ser


class TestPodcastSerializerRSS(unittest.TestCase):
    def setUp(self):
        self.author = Author(name="John Doe", email="john@doe.com")
        self.episode1 = Episode(
            id=1,
            title="Episode 1",
            description="Episode 1: test.",
            audio_file="episode1.mp3",
        )
        self.episode2 = Episode(
            id=2,
            title="Episode 2",
            description="Episode 2: second test.",
            audio_file="episode2.mp3",
        )
        self.podcast = Podcast(
            title="Test podcast",
            subtitle="Test podcast subtitle.",
            description="Test podcast description.",
            author=self.author,
            episodes=[self.episode1, self.episode2],
            base_url="https://example.com",
        )

    def tearDown(self):
        pass

    def test_podcast_serializer(self):
        output = ser.PodcastEnconderRSS.serialize(self.podcast)

        fg = FeedGenerator()
        fg.load_extension("podcast")
        # fg.podcast.itunes_category("Technology", "Podcasting")
        fg.title("Test podcast")
        fg.description("Test podcast description.")
        fg.author({"name": "John Doe", "email": "john@doe.com"})
        fg.link(href="https://example.com/podcast.atom", rel="self")
        fg.logo("https://example.com/podcast.jpg")

        for episode in (self.episode1, self.episode2):
            fe = fg.add_entry()
            media_url = "https://example.com/{}/audio.mp3".format(episode.id)
            fe.id(media_url)
            fe.title(episode.title)
            fe.description(episode.description)
            fe.enclosure(media_url, 0, "audio/mpeg")

        expected_output = fg.rss_str(pretty=False).decode("utf-8")

        self.assertEqual(output, expected_output)
