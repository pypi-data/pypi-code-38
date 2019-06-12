from flywheel_cli.walker import AbstractWalker, FileInfo

class MockWalker(AbstractWalker):
    def _listdir(self, path):
        results = getattr(self, 'results', [])
        for result in results:
            yield result

    def open(self, path, mode='rb', **kwargs):
        raise FileNotFoundError('File not found!')

    def get_fs_url(self):
        return self.root

def test_should_include_file():
    def should_include(fname, includes=None, excludes=None):
        walker = MockWalker('/', filter=includes, exclude=excludes)
        return walker._should_include_file(FileInfo(fname, False))

    assert should_include('test.txt')
    assert not should_include('.test')

    assert should_include('test.txt', includes=['*.txt'])
    assert not should_include('test.csv', includes=['*.txt'])
    assert should_include('test.csv', includes=['test.*'])
    assert should_include('test.csv', includes=['*.txt', '*.csv'])

    assert not should_include('test.txt', excludes=['*.txt'])
    assert should_include('test.csv', excludes=['*.txt'])

    assert should_include('foo.txt', includes=['*.txt'], excludes=['test.*'])
    assert not should_include('test.txt', includes=['*.txt'], excludes=['test.*'])


def test_should_include_directory():
    def should_include(dpath, includes=None, excludes=None):
        _, _, dname = dpath.rpartition('/')
        walker = MockWalker('/', filter_dirs=includes, exclude_dirs=excludes)
        return walker._should_include_dir('/' + dpath, FileInfo(dname, True))

    assert should_include('test')
    assert not should_include('.test')

    assert should_include('test', includes=['test'])
    assert should_include('test/foo', includes=['test'])
    assert not should_include('foo', includes=['test'])

    assert should_include('test', excludes=['foo'])
    assert should_include('test/bar', excludes=['foo'])
    assert not should_include('foo', excludes=['foo'])
    assert not should_include('test/foo', excludes=['foo'])

def test_combine_paths():
    walker = MockWalker('/')
    assert walker.combine('/', '/foo') == '/foo'
    assert walker.combine('foo/', '/bar') == 'foo/bar'
    assert walker.combine('foo', 'bar') == 'foo/bar'
    assert walker.combine('/foo', 'bar/') == '/foo/bar/'
