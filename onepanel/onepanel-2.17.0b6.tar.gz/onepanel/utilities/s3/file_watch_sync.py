import os

from watchdog.events import PatternMatchingEventHandler

from onepanel.utilities.s3.file_sync import FileDifference, FileEvent


class FileWatchSynchronizerEventHandler(PatternMatchingEventHandler):
    def __init__(self, path, remote_path, synchronizer, ignore_patterns=None):
        """

        :param path:
        :param remote_path:
        :param synchronizer:
        :type synchronizer onepanel.utilities.s3.file_sync.ThreadedFileSynchronizer
        :param hook:
        """

        PatternMatchingEventHandler.__init__(self, ignore_patterns=ignore_patterns)

        self.path = path
        self.path_length = len(path) + 1
        self.remote_path = remote_path
        self.synchronizer = synchronizer

    def on_created(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        destination_path = os.path.join(self.remote_path, relative_path)

        difference = FileDifference(event.src_path, destination_path, FileDifference.State.NEW)
        self._synchronize_difference(difference)

    def on_moved(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]
        relative_destination = event.dest_path[self.path_length:]

        if self.should_skip(relative_path) or self.should_skip(relative_destination):
            return

        original_destination = os.path.join(self.remote_path, relative_path)
        destination = os.path.join(self.remote_path, relative_destination)

        difference = FileDifference(event.dest_path,
                                    destination,
                                    FileDifference.State.MOVED,
                                    event.src_path,
                                    original_destination)

        self._synchronize_difference(difference)

    def on_deleted(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        destination_path = os.path.join(self.remote_path, relative_path)

        difference = FileDifference(event.src_path, destination_path, FileDifference.State.DELETED)
    
        self._synchronize_difference(difference)

    def on_modified(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        destination_path = os.path.join(self.remote_path, relative_path)
        difference = FileDifference(event.src_path, destination_path, FileDifference.State.MODIFIED)
        self._synchronize_difference(difference)

    def _synchronize_difference(self, difference):
        self.synchronizer.synchronize_single(difference)

    def should_skip(self, relative_path):
        # Ignore vim temporary file and mac temporary files
        return relative_path[-1] == '~' or '.sb' in relative_path


