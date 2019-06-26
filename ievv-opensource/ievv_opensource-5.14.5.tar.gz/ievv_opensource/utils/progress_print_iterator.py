from django.utils import timezone


class ProgressPrintIterator:
    """
    Progress print iterator. Useful to print progress of long running scripts.

    Example::

        queryset = MyModel.objects
        total = queryset.count()
        for obj, is_end_of_group in ProgressPrintIterator(
                iterator=queryset.iterator(),
                total_count=total,
                what='Doing something',
                items_per_group=500):
            # Do something with ``obj``. If you want to do something after 500 items has been processed
            # including the last iteration (which may be less than 500 items),
            # use ``if is_end_of_group``
    """
    def __init__(self, iterator, total_count, what, items_per_group=500, log_function=None):
        """

        Args:
            iterator: Some iterator, such as a ``queryset.iterator()``.
            total_count: Total number of items.
            what: A message to print when printing progress
            items_per_group: Items per group - we print progress each time we have processed this number of items.
            log_function: A log function. For management scripts, you want to set this to ``self.stdout.write``.
        """
        self.iterator = iterator
        self.total_count = total_count
        self.what = what
        self.items_per_group = items_per_group
        self.log_function = log_function or print

    def __iter__(self):
        start_time = timezone.now()
        for index, item in enumerate(self.iterator, start=1):
            progress_percent = index / self.total_count * 100
            is_end_of_group = (index % self.items_per_group == 0) or (index == self.total_count)
            yield item, is_end_of_group
            if is_end_of_group:
                now = timezone.now()
                time_used = now - start_time
                if progress_percent > 0:
                    estimated_end_delta = time_used / progress_percent * (100 - progress_percent)
                    estimated_end_minutes = round(estimated_end_delta.total_seconds() / 60, 2)
                else:
                    estimated_end_minutes = 'UNKNOWN'
                self.log_function(
                    f'{round(progress_percent, 1)}% [{index}/{self.total_count}]: {self.what}. '
                    f'Est. minutes remaining: {estimated_end_minutes}')
