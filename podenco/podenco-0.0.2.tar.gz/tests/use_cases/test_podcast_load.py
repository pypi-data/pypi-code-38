#!/usr/bin/env python

import unittest
import unittest.mock as mock

from podenco.domain.podcast import Podcast, Author, Episode
from podenco.use_cases.podcast_load import PodcastLoad


class TestPodcastLoad(unittest.TestCase):
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

    def test_case(self):
        repo = mock.Mock()
        repo.get.return_value = self.podcast

        podcast_load_use_case = PodcastLoad(repo)
        result = podcast_load_use_case.execute()

        repo.podcast.asset_called_with()
        self.assertEqual(result, self.podcast)
