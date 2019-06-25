#!/usr/bin/env python

import os
import tempfile

import unittest
import unittest.mock as mock

from podenco.domain.podcast import Podcast, Author, Episode
from podenco.serializers import podcast_serializer_rss as ser
from podenco.use_cases.podcast_generate import PodcastGenerate


class TestPodcastLoad(unittest.TestCase):
    def setUp(self):
        self.input_path = tempfile.TemporaryDirectory()

        tmp_dir = self.input_path.name

        with open(tmp_dir + "/episode1.mp3", "wb") as f:
            f.write(b"episode_1_mp3_content")

        with open(tmp_dir + "/episode2.mp3", "wb") as f:
            f.write(b"episode_2_mp3_content")

        self.author = Author(name="John Doe", email="john@doe.com")
        self.episode1 = Episode(
            id=1,
            title="Episode 1",
            description="Episode 1: test.",
            audio_file=tmp_dir + "/episode1.mp3",
        )
        self.episode2 = Episode(
            id=2,
            title="Episode 2",
            description="Episode 2: second test.",
            audio_file=tmp_dir + "/episode2.mp3",
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
        self.input_path.cleanup()

    def test_podcast_generate(self):
        repo = mock.Mock()
        repo.get.return_value = self.podcast

        with tempfile.TemporaryDirectory() as tmpdirname:
            podcast_generate_use_case = PodcastGenerate(
                repository=repo, output_path=tmpdirname + "/podcast"
            )
            podcast_generate_use_case.execute()

            self.assertTrue(os.path.exists(tmpdirname + "/podcast"))

            with open(tmpdirname + "/podcast/podcast.rss") as f:
                rss_content = f.read()
                expected_output = ser.PodcastEnconderRSS.serialize(self.podcast)
                self.assertEqual(rss_content, expected_output)

            self.assertTrue(os.path.exists(tmpdirname + "/podcast/1/audio.mp3"))

            with open(tmpdirname + "/podcast/1/audio.mp3", "rb") as f:
                audio_content = f.read()
                self.assertEqual(audio_content, b"episode_1_mp3_content")

            self.assertTrue(os.path.exists(tmpdirname + "/podcast/2/audio.mp3"))

            with open(tmpdirname + "/podcast/2/audio.mp3", "rb") as f:
                audio_content = f.read()
                self.assertEqual(audio_content, b"episode_2_mp3_content")
