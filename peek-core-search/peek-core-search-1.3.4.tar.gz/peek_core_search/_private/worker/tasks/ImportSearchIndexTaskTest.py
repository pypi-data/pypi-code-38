import unittest

from peek_core_search._private.worker.tasks.ImportSearchIndexTask import _splitKeywords


class ImportSearchIndexTaskTest(unittest.TestCase):
    def testKeywordSplit(self):
        self.assertEqual(_splitKeywords("ZORRO-REYNER"), {'zorroreyner'})
        self.assertEqual(_splitKeywords("34534535"), {'34534535'})


if __name__ == '__main__':
    unittest.main()
