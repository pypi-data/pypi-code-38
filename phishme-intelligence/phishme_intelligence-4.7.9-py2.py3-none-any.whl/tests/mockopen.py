import io
import mock
import sys
from contextlib import contextmanager


class OpenMock(object):
    def __init__(self, watched_files):
        # import pdb; pdb.set_trace()
        """Initialize an OpenMock object
        Args:
            watched_files - a dictionary of filenames to return values

            The return values can either be a string or a tuple of strings

            If you pass a string that value will be returned everytime
            open is called with that file
            Ex:
            {'test.txt': 'File contents.'}

            Every time that file is opened it will get 'File contents.'

            If you pass a tuple of return values then each time the
            file is open the next value in the tuple is returned
            If the file is open more times than there are values in
            the tuple then it will not be mocked

            Ex:
            {'test.txt': ('First open', 'Second open')}

            The first time the file is opened it will return 'First open'
            the second time it will return 'Second open'
            the third time and on it will use the real builtin

            If you want to simulate a file not found error you can
            specify 'IOError' as the output.
            This can be done as a string
            {'test.txt': 'IOError'}
            this will always raise an IOError

            It can also be in the tuple of values
            {'test.txt': ('IOError', 'Success!')}
            this will raise an IOError the first open and return 'Success!'
            the second time the file is open

        """
        self.files_opened = []
        self.watched_files = watched_files

    def _is_watched_file(self, filename):
        return filename in self.watched_files.keys

    def file_open_count(self, filename):
        return len([f for f in self.files_opened if f[0] is filename])

    def file_was_open(self, filename):
        return self.file_open_count(filename) > 0

    def file_was_open_with(self, filename, *args, **kwargs):
        return len([f for f in self.files_opened if f[0] is filename and f[1] == args and f[2] == kwargs]) > 0

    @contextmanager
    def mock_open(self):
        """Mock the open() builtin function on a specific  filename
        """
        def mock_file(*args, **kwargs):
            # get the filename
            filename = args[0]

            # get the number of times this file was opened
            # need to do this before appending to files_opened
            times_opened = self.file_open_count(filename)
            # print('[times_openes] %d' % times_opened)
            # track the files that have been opened
            self.files_opened.append((filename, args[1:], kwargs))

            # mocked_file.stop()
            # import pdb; pdb.set_trace()
            # mocked_file.start()

            # Only work with watched files.
            # If just a string was given as input then that will always be the return value.
            # If a tuple was given then each time the file is open the content will be the next value in the tuple.
            # If there are no more values availale in the tuple the file will be ignored and opened normally
            if filename in self.watched_files.keys() and (isinstance(self.watched_files[filename], str) or len(self.watched_files[filename]) > times_opened):
                # Get the contents to return
                contents = self.watched_files[filename] if isinstance(self.watched_files[filename], str) else self.watched_files[filename][times_opened]
                # print('[contents] %s' % contents)
                # Need to decode utf-8 only if we're running python 2.x
                contents = contents.decode('utf-8') if sys.version_info[0] == 2 else contents

                # if the number of times the file has been opened exceeds the outputs
                if contents == 'IOError':
                    raise IOError('does not exist')
                f = io.StringIO(contents)
                f.name = filename
            else:

                # If the file isn't watched then we'll stop mocking, open the file then start mocking again
                mocked_file.stop()
                f = open(*args, **kwargs)
                mocked_file.start()
            return f

        # If we're using python 2.x then we need to mock __builtin__.open, for python 3.x it's just builtin.open
        mocked_file = mock.patch('__builtin__.open', mock_file) if sys.version_info[0] == 2 else mock.patch('builtins.open', mock_file)
        mocked_file.start()
        yield
        mocked_file.stop()
