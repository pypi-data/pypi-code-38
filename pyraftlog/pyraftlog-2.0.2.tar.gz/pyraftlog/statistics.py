from collections import deque


class Statistics:
    """
    Manages a queue of Sample objects to provide statistics.
    """

    def __init__(self, max_size=100):
        """
        Instantiate a new instance of the Statistics class

        :param max_size: The maximum amount of samples to keep
        :type max_size: int
        """
        self._queue = deque(maxlen=max_size)
        self._samples = {}

    def _is_sample_complete(self, sample_index):
        """
        Checks whether the Sample object is complete or not.

        :return: True if Sample is full, otherwise false
        :rtype: bool
        """
        return self._samples[sample_index].full_sample()

    def _add_sample(self, sample_index):
        """
        Adds the self.sample to the queue, will remove the oldest sample if queue is full.

        :param sample_index: Sample index
        :type sample_index: int
        :rtype: None
        """
        self._queue.append(self._samples[sample_index])
        self._samples.pop(sample_index)

    def generate_statistics(self):
        """
        Generate a set of statistics using available samples.

        :return: A dictionary containing the generated statistics
        :rtype: dict
        """
        response = {}
        response_times = []
        commit_times = []
        apply_times = []
        # Freeze the samples before iterating
        for sample in list(self._queue):
            response_times.append(sample.responded_timestamp - sample.append_timestamp)
            commit_times.append(sample.committed_timestamp - sample.append_timestamp)
            apply_times.append(sample.applied_timestamp - sample.append_timestamp)

        if response_times:
            response['sample_size'] = len(response_times)
            response['avg_response_time'] = sum(response_times) / len(response_times)
            response['avg_commit_times'] = sum(commit_times) / len(commit_times)
            response['avg_apply_times'] = sum(apply_times) / len(apply_times)

        return response

    def set_append_timestamp(self, sample_index, timestamp):
        """
        Set the append timestamp for the current Sample.

        :param sample_index: The log entry index for this Sample
        :param timestamp: The time
        :type sample_index: int
        :type timestamp: float
        :rtype: None
        """
        if sample_index not in self._samples:
            self._samples[sample_index] = Sample(sample_index)

        try:
            self._samples[sample_index].append_timestamp = timestamp
            if self._is_sample_complete(sample_index):
                self._add_sample(sample_index)
        except KeyError:
            pass

    def set_responded_timestamp(self, sample_index, timestamp):
        """
        Set the responded timestamp for the current Sample.

        :param sample_index: The log entry index for this Sample
        :param timestamp: The time
        :type sample_index: int
        :type timestamp: float
        :rtype: None
        """
        if sample_index not in self._samples:
            return

        try:
            self._samples[sample_index].responded_timestamp = timestamp
            if self._is_sample_complete(sample_index):
                self._add_sample(sample_index)
        except KeyError:
            pass

    def set_committed_timestamp(self, sample_index, timestamp):
        """
        Set the committed timestamp for the current Sample.

        :param sample_index: The log entry index for this Sample
        :param timestamp: The time
        :type sample_index: int
        :type timestamp: float
        :rtype: None
        """
        if sample_index not in self._samples:
            return

        try:
            self._samples[sample_index].committed_timestamp = timestamp
            if self._is_sample_complete(sample_index):
                self._add_sample(sample_index)
        except KeyError:
            pass

    def set_applied_timestamp(self, sample_index, timestamp):
        """
        Set the applied timestamp for the current Sample.

        :param sample_index: The log entry index for this Sample
        :param timestamp: The time
        :type sample_index: int
        :type timestamp: float
        :rtype: None
        """
        if sample_index not in self._samples:
            return

        try:
            self._samples[sample_index].applied_timestamp = timestamp
            if self._is_sample_complete(sample_index):
                self._add_sample(sample_index)
        except KeyError:
            pass


class Sample:
    """
    Class to hold timestamps of when different events occurred to allow the generation of statistics.
    """

    def __init__(self, index):
        """
        Create a new instance of a Sample object.

        :param index: The index of the log entry these timestamps relate to
        :type index: int
        """
        self.index = index
        self.append_timestamp = None
        self.responded_timestamp = None
        self.committed_timestamp = None
        self.applied_timestamp = None

    def __str__(self):
        return '''
                Index: %s
                Appended at %s
                Responded at %s
                Committed at %s
                Applied at %s
                ''' % (self.index,
                       self.append_timestamp,
                       self.responded_timestamp,
                       self.committed_timestamp,
                       self.applied_timestamp)

    def full_sample(self):
        """
        Checks whether this sample has all the required timestamps.

        :return: True if all timestamps filled out, otherwise false
        :rtype: bool
        """
        if self.append_timestamp and \
                self.responded_timestamp and \
                self.committed_timestamp and \
                self.applied_timestamp:
            return True
        else:
            return False
