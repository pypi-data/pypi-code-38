#!/usr/bin/env python
import unittest

from podenco.domain.podcast import Podcast, Author, Episode


class TestAuthor(unittest.TestCase):
    def test_init_author(self):
        author = Author(name="John Doe", email="john@doe.com")
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.email, "john@doe.com")

    def test_author_to_dict(self):
        author = Author(name="John Doe", email="john@doe.com")
        self.assertEqual(
            author.to_dict(), {"name": "John Doe", "email": "john@doe.com"}
        )


class TestEpisode(unittest.TestCase):
    def test_init_episode(self):
        episode = Episode(
            id=1,
            title="Episode 1",
            description="Episode 1: test.",
            audio_file="episode1.mp3",
        )
        self.assertEqual(episode.id, 1)
        self.assertEqual(episode.title, "Episode 1")
        self.assertEqual(episode.description, "Episode 1: test.")
        self.assertEqual(episode.audio_file, "episode1.mp3")


class TestPodcasts(unittest.TestCase):
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

    def test_init_podcast(self):
        podcast = Podcast(
            title="Test podcast",
            subtitle="Test podcast subtitle.",
            description="Test podcast description.",
            author=self.author,
            episodes=[self.episode1, self.episode2],
            base_url="https://example.com",
        )
        self.assertEqual(podcast.title, "Test podcast")
        self.assertEqual(podcast.subtitle, "Test podcast subtitle.")
        self.assertEqual(podcast.description, "Test podcast description.")
        self.assertEqual(podcast.author, self.author)
        self.assertEqual(podcast.episodes, [self.episode1, self.episode2])
        self.assertEqual(podcast.base_url, "https://example.com")
        self.assertEqual(podcast.atom_url, "https://example.com/podcast.atom")
        self.assertEqual(podcast.rss_url, "https://example.com/podcast.rss")
        self.assertEqual(podcast.logo_url, "https://example.com/podcast.jpg")

    def test_episode_media_url(self):
        podcast = Podcast(
            title="Test podcast",
            subtitle="Test podcast subtitle.",
            description="Test podcast description.",
            author=self.author,
            episodes=[self.episode1, self.episode2],
            base_url="https://example.com",
        )
        self.assertEqual(
            podcast.episode_audio_url(self.episode1), "https://example.com/1/audio.mp3"
        )
