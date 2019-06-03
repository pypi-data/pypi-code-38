import unittest


def test_data(*paths):
    from os.path import dirname, join, abspath

    return abspath(join(dirname(__file__), 'test_data', *paths))


def cache_fs():
    from fs.tempfs import TempFS

    return TempFS('rowgenerator')


def get_cache():
    return cache_fs()


class MetapackTest(unittest.TestCase):
    """Test Metapack AppUrls and Row Generators"""

    def setUp(self):
        import warnings
        warnings.simplefilter('ignore')
