from itertools import cycle
import logging
import dateutil.parser
from datetime import datetime, timedelta
from pprint import pprint, pformat
import threading
import time
import typing


class APITokenBudgeter(object):
    """
    A class to ration API tokens for HockeyApp.

    HockeyApp API tokens are rate limited to 60 requests per minute.
    This class rations out API tokens round-robin and LRU based on a list of valid tokens.
    If all have been "spent" (all have been used `api_rate` times in the last `api_rate_period`), then
    sleep the shortest time.

    To use this, initialize it, then treat it like an iterator.

    The more API tokens you provide, the more parallelization, up to about 10 tokens.
    """

    def __init__(self,
                 tokens,
                 api_rate: int=60,
                 api_rate_period: timedelta=None) -> None:
        """
        Prepare the budgeter.
        :param tokens: an iterable of API tokens.
        :param api_rate: How many API calls you can make with each token, per minute.
                         Default is 60 requests per minute.
        """
        self.api_tokens = tokens # type:typing.List[str]
        self.api_rate = api_rate
        self.api_rate_period = api_rate_period or timedelta(minutes=1)
        self.last_usage_by_token = {t: [] for t in tokens} # type:typing.Dict[str,typing.List[datetime]]
        self.lock = threading.Lock()
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        return self

    def _cull_old_usages(self) -> None:
        """
        Forgets about API usages that are over one minute ago.
        :return: None
        """
        # delete uses older than a minute
        self.log.info("Culling")
        cutoff = datetime.now() - self.api_rate_period
        for apikey in self.api_tokens:
            uses = self.last_usage_by_token[apikey]
            before_cull_length = len(uses)
            uses[:] = [use for use in uses if use >= cutoff]
            self.log.debug("Culling: %d->%d for key %s", before_cull_length, len(uses), apikey)
            if len(uses) == before_cull_length and before_cull_length == self.api_rate:
                self.log.warning("could not cull any usages for key %s", apikey)

    def _find_unused_key(self) -> typing.Optional[str]:
        for apikey in self.api_tokens:
            uses = self.last_usage_by_token[apikey]
            # uses is a list of datetimes, "oldest" at front
            if len(uses) < self.api_rate:
                uses.append(datetime.now())
                return apikey
        return None

    def _sleep_shortest(self) -> None:
        """
        This blocks until at least one API token is ready for re-use.
        :return: None
        """
        firsts = [v[0] for v in self.last_usage_by_token.values() if len(v) > 0]
        assert len(firsts) > 0, "there must be something tokens issued or nothing to sleep"
        ascending = sorted(firsts)
        # sleep until ascending[0]+self.api_rate_period
        oldest = ascending[0]
        assert ascending[0] < datetime.now()
        delta = (oldest + self.api_rate_period) - datetime.now()
        if (delta.total_seconds() <= 0): # Round up.
            delta = timedelta(seconds=1)
        assert delta.total_seconds() >= 0, "can't sleep negative seconds (delta={0})".format(delta.total_seconds())
        self.log.info("oldest is %s, sleeping for %f sec", str(oldest), delta.total_seconds())
        time.sleep(delta.total_seconds())

    def dumpState(self):
        self.log.debug("{0} API tokens.".format(len(self.api_tokens)))
        self.log.debug(pformat(self.last_usage_by_token))

    def __next__(self):
        return self.next()

    def next(self) -> str:
        '''
        Return a HockeyApp API Token that is "valid" (not overused or rate-limited yet)
        HockeyApp API guide says: "We limit requests to 60 per minute and App ID. If the limit is exceeded, please throttle your script or contact us."
        '''
        with self.lock:
            k = self._find_unused_key()
            if k is not None:
                return k
            self._cull_old_usages()
            k = self._find_unused_key()
            if k is not None:
                return k
            # TODO let go of the lock while sleeping, don't block all of the thread using `self`.
            self._sleep_shortest()
            self._cull_old_usages()
            k = self._find_unused_key()
            if k is not None:
                return k
            raise RuntimeError("Cannot find unused keys after slumbering. Programmer error!")
