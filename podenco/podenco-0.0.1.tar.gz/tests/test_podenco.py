#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `podenco` package."""


import unittest
from unittest.mock import patch, mock_open

from click.testing import CliRunner

from podenco.domain.podcast import Podcast, Author, Episode
from podenco.repositories.yaml_repository import YamlRepository
from podenco import cli


class Testpodenco(unittest.TestCase):
    """Tests for `podenco` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help  Show this message and exit." in help_result.output
        assert "generate  Generate static site file structure." in help_result.output

    @patch("podenco.cli.PodcastGenerate")
    def test_cli_generate(self, MockPodcastGenerate):
        """Test the CLI."""
        runner = CliRunner()

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

        mock_podcast_generate = MockPodcastGenerate.return_value

        with patch("builtins.open", mock_open(read_data=yaml_str)) as yaml_file:
            result = runner.invoke(cli.generate, ["podcast.yaml", "/output/"])
            yaml_file.assert_called_with("podcast.yaml")

        MockPodcastGenerate.assert_called_once_with(repository, "/output/")
        mock_podcast_generate.execute.assert_called_once()

        assert result.exit_code == 0
        assert result.output == "Done!\n"
