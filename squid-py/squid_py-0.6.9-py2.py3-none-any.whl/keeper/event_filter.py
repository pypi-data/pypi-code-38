import logging
import time

logger = logging.getLogger(__name__)


class EventFilter:
    def __init__(self, event_name, event, argument_filters, from_block, to_block, poll_interval=None):
        self.event_name = event_name
        self.event = event
        self.argument_filters = argument_filters
        self.block_range = (from_block, to_block)
        self._filter = None
        self._poll_interval = poll_interval
        self._create_filter()

    def set_poll_interval(self, interval):
        self._poll_interval = interval

    def recreate_filter(self):
        self._create_filter()

    def _create_filter(self):
        self._filter = self.event().createFilter(
            fromBlock=self.block_range[0],
            toBlock=self.block_range[1],
            argument_filters=self.argument_filters
        )
        if self._poll_interval is not None:
            self._filter.poll_interval = self._poll_interval

    def get_new_entries(self, max_tries=1):
        return self._get_entries(self._filter.get_new_entries, max_tries=max_tries)

    def get_all_entries(self, max_tries=1):
        return self._get_entries(self._filter.get_all_entries, max_tries=max_tries)

    def _get_entries(self, entries_getter, max_tries=1):
        i = 0
        while i < max_tries:
            try:
                logs = entries_getter()
                if logs:
                    return logs
            except ValueError as e:
                # logger.debug(f'Got error fetching event logs: {str(e)}')
                if 'Filter not found' in str(e):
                    self._create_filter()
                else:
                    raise

            i += 1
            time.sleep(0.01)

        return []
