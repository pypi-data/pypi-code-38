#!/usr/bin/env python

import unittest

from podenco.domain.podcast import Podcast, Author, Episode
from podenco.repositories.yaml_repository import YamlRepository


class TestYamlRepository(unittest.TestCase):
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

    def test_get(self):
        yaml_str = """---
podcast:
    title: Test podcast
    subtitle: Test podcast subtitle.
    description: Test podcast description.
    author:
        name: John Doe
        email: john@doe.com
    episodes:
        - title: Episode 1
          description: "Episode 1: test."
          audio_file: episode1.mp3
        - title: Episode 2
          description: "Episode 2: second test."
          audio_file: episode2.mp3
    base_url: https://example.com
"""
        repository = YamlRepository(yaml_str)
        result = repository.get()

        self.assertEqual(result, self.podcast)
