import csv
import feedparser
import os
import shutil
import tempfile
import unittest

from slapos.resilient.rdiffBackupStat2RSS import genRSS

class Option(dict):
    def __init__(self, **kw): 
        self.__dict__.update(kw)
    def __setitem__(i, y):
        self.__dict__[i] = y

class TestRdiffBackupStat2RSS(unittest.TestCase):
  def setUp(self):
    self.data_directory = tempfile.mkdtemp(dir='.')
    self.feed_path = os.path.join(self.data_directory)

  def tearDown(self):
    shutil.rmtree(self.data_directory)

  def getOptionObject(self, **kw):
    """
    Returns an object containing options as properties, to simulate a call
    to the tested script
    """
    option = {
      'rdiff_backup_data_folder': self.data_directory,
      'output': self.feed_path,
      'feed_url': 'http://exemple.com',
    }
    option.update(kw)
    return Option(**option)

  def createSample(self):
    """
    Writes 2 statistics file in rdiff-backup format
    """
    with open(os.path.join(self.data_directory, 'session_statistics_1'), 'w') as stat_file:
      stat_file.write("""\
        StartTime 1473339659.00 (Thu Sep  8 15:00:59 2016)
        EndTime 1473339667.81 (Thu Sep  8 15:01:07 2016)
        ElapsedTime 8.81 (8.81 seconds)
        SourceFiles 2381
        SourceFileSize 142096473 (136 MB)
        MirrorFiles 1
        MirrorFileSize 0 (0 bytes)
        NewFiles 2380
        NewFileSize 142096473 (136 MB)
        DeletedFiles 0
        DeletedFileSize 0 (0 bytes)
        ChangedFiles 1
        ChangedSourceSize 0 (0 bytes)
        ChangedMirrorSize 0 (0 bytes)
        IncrementFiles 0
        IncrementFileSize 0 (0 bytes)
        TotalDestinationSizeChange 142096473 (136 MB)
        Errors 0""")
    with open(os.path.join(self.data_directory, 'session_statistics_2'), 'w') as stat_file:
      stat_file.write("""\
        StartTime 1473340154.00 (Thu Sep  8 15:09:14 2016)
        EndTime 1473340154.95 (Thu Sep  8 15:09:14 2016)
        ElapsedTime 0.95 (0.95 seconds)
        SourceFiles 2381
        SourceFileSize 142096473 (136 MB)
        MirrorFiles 2381
        MirrorFileSize 142096473 (136 MB)
        NewFiles 0
        NewFileSize 0 (0 bytes)
        DeletedFiles 0
        DeletedFileSize 0 (0 bytes)
        ChangedFiles 15
        ChangedSourceSize 230112 (225 KB)
        ChangedMirrorSize 230112 (225 KB)
        IncrementFiles 15
        IncrementFileSize 2122 (2.07 KB)
        TotalDestinationSizeChange 2122 (2.07 KB)
        Errors 0""")

  def test_generatedRSSIsCorrect(self):
    self.createSample()
    option = self.getOptionObject()
    feed_content = genRSS(option)
    feed = feedparser.parse(feed_content)

    self.assertFalse(feed.bozo)
    self.assertTrue(len(feed.entries), 2)
    self.assertLess(feed.entries[0].published_parsed, feed.entries[1].published_parsed)


if __name__ == '__main__':
  unittest.main()
