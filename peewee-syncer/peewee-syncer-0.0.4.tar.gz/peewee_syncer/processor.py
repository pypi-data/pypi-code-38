import time
import itertools
import logging
from collections import deque

log = logging.getLogger('peewee_syncer')

class LastOffsetQueryIterator:
    def __init__(self, i, row_output_fun, key_fun, is_unique_key=False):
        self.iterator = i
        self.n = 0
        self.row_output_fun = row_output_fun
        self.last_updates = deque([None], maxlen=2)
        self.key_fun = key_fun
        self.is_unique_key = is_unique_key

    def get_last_offset(self, limit):
        # log.debug("Offsets {} n={} limit={}".format(self.last_updates, self.n, limit))
        if self.n == limit and not self.is_unique_key:
            return self.last_updates[0]
        else:
            return self.last_updates[-1]

    def iterate(self):
        for row in self.iterator:
            self.n = self.n + 1

            value = self.key_fun(row)
            if self.last_updates[-1] != value:
                self.last_updates.append(value)

            output = self.row_output_fun(row)
            if output:
                yield output


class Processor:
    def __init__(self, sync_manager, it_function, process_function, sleep_duration=3):
        self.it_function = it_function
        self.process_function = process_function
        self.sync_manager = sync_manager
        self.sleep_duration = sleep_duration


    def process(self, limit, i):

        for n in itertools.count():

            if i > 0 and n == i:
                log.debug("Stopping after iteration {}".format(n))
                break

            last_offset = self.sync_manager.get_last_offset()

            it = self.it_function(since=last_offset['value'], limit=limit)

            self.process_function(it.iterate())

            if self.sync_manager.is_test_run:
                log.debug("Stopping after iteration (test in progress). Processed {} records".format(it.n))
                break

            final_offset = it.get_last_offset(limit=limit)

            if it.n == 0:
                time.sleep(self.sleep_duration)
                log.debug("Caught up, sleeping..")
            else:
                log.debug("Processed records n={} offset={}".format(it.n, final_offset if final_offset else "unchanged"),
                               extra={'n': it.n, 'offset': final_offset})

                if final_offset != last_offset['value']:
                    if final_offset:
                        self.sync_manager.set_last_offset(final_offset, 0)
                else:
                    time.sleep(self.sleep_duration)
                    # todo: if behind current time then abort on second attempt
                    # this would prevent stuck in loop due to bulk updates
                    log.warning("Final offset remains unchanged")

                with self.sync_manager.get_db().connection_context():
                    self.sync_manager.save()

        log.info("Completed processing")

