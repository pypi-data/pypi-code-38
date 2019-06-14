import csv
import os
import shutil
import tempfile
import unittest

import twitter_fire_scraper
from twitter_fire_scraper.scraper import Scraper
from twitter_fire_scraper.tests.test.incur_api_hits.cached_tweets import CachedTweets


class TestFileSaving(unittest.TestCase):

    def count_statuses(self, statuses):
        total_statuses = 0
        for keyword, statuses in statuses.items():
            for status in statuses:
                total_statuses += 1

        return total_statuses

    def setUp(self):
        # Temp folder for CSV files
        self.temp_folder = os.path.join(tempfile.gettempdir(), twitter_fire_scraper.__name__, TestFileSaving.__name__)

        # Scraper for scraping
        self.scraper = CachedTweets.scraper

        # Assorted filetype dirs
        self.csv_folder = os.path.join(self.temp_folder, 'csv')
        self.json_folder = os.path.join(self.temp_folder, 'json')

        os.makedirs(self.temp_folder, exist_ok=True)
        os.makedirs(self.csv_folder, exist_ok=True)
        os.makedirs(self.json_folder, exist_ok=True)

        print("Saved CSV files from test cases can be found at:")
        print(self.temp_folder)

    def testSaveCSVSmall(self):
        """Tests that the scraper can produce small CSV files."""
        tweets = CachedTweets.tweets_small_geo()

        tweets_csv_path = os.path.join(self.csv_folder, 'tweets_small.csv')

        self.scraper.save_statusdict_to_csv(tweets, tweets_csv_path, overwrite=True)

        total_lines = 0
        with open(tweets_csv_path, 'r', encoding='utf-16') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=Scraper.CSV_DELIMITER)
            for row in csv_reader:
                total_lines += 1

        total_statuses = self.count_statuses(tweets)

        # We should have as many tweets as there are lines in the file, plus one for the header.
        self.assertEqual(total_lines, total_statuses + 1)

    def testSaveCSVNoRetweets(self):
        """Tests that the scraper can produce a CSV file with absolutely no retweets."""
        tweets = CachedTweets.tweets_medium_no_retweets()

        tweets_csv_path = os.path.join(self.csv_folder, 'tweets_medium_noretweets.csv')

        self.scraper.save_statusdict_to_csv(tweets, tweets_csv_path, overwrite=True)

        total_lines = 0
        with open(tweets_csv_path, 'r', encoding='utf-16') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=Scraper.CSV_DELIMITER)
            for row in csv_reader:
                total_lines += 1

        total_statuses = self.count_statuses(tweets)

        # We should have as many tweets as there are lines in the file, plus one for the header.
        assert (total_lines == (total_statuses + 1))

    def testSaveCSVLarge(self):
        """Tests that the scraper can produce large CSV files."""
        tweets = CachedTweets.tweets_large_geo()

        tweets_csv_path = os.path.join(self.csv_folder, 'tweets_large.csv')

        self.scraper.save_statusdict_to_csv(tweets, tweets_csv_path, overwrite=True)

        total_lines = 0
        with open(tweets_csv_path, 'r', encoding='utf-16') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=Scraper.CSV_DELIMITER)
            for row in csv_reader:
                total_lines += 1

        total_statuses = self.count_statuses(tweets)

        # We should have as many tweets as there are lines in the file, plus one for the header.
        self.assertEqual(total_lines, (total_statuses + 1))
