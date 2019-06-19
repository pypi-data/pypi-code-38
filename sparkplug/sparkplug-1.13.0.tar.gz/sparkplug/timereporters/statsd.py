"""
Sends timing information to Datadog custom metrics

    [time_reporter:statsdtimer]
    # which class to instance?
    use = sparkplug#statsd
    # How many samples to combine during each reporting period,
    # since Datadog aggregates the data itself, we don't need to.
    aggregation_count = 1
    # Tags to help with reporting:
    tags = service:myconsumer
    # Any extra parameters will be passed to statsdecor
    port = 8125
    host = localhost
    vendor = datadog

    [consumer:myconsumer]
    <blah>
    # I could use multiple timers like this: time_reporters = statsdtimer, myothertimer
    time_reporters = statsdtimer

Parameters:
    aggregation_count : integer, required, same as base class:
      number of samples to combine before reporting
    tags : list or None, optional, the list of key:value tags to associate
      with the sample sent to datadog
    extra parameters will be sent to the underlying statsdecor module, e.g.:
        port
        host
        vendor

"""

from sparkplug.logutils import LazyLogger
_log = LazyLogger(__name__)

from sparkplug.timereporters.base import Base, min_median_max

try:
    # pip install statsdecor
    import statsdecor

    class Statsd(Base):
        def __init__(self, aggregation_count, tags=None, **kwargs):
            super(Statsd, self).__init__(aggregation_count)

            self.exec = []
            self.erro = []
            self.wait = []

            conf = {"prefix": "sparkplug"}
            conf.update(kwargs)
            # Don't share the global client, we might be
            # configured differently than the global:
            self.statsd = statsdecor._create_client(**conf)

            self.tags = self._parse_tags(tags)

        def _parse_tags(self, tags):
            ret = None
            if tags:
                ret = [x.strip() for x in tags.split(',')]
            return ret

        def append_exec(self, delta):
            self.exec.append(delta)
            if len(self.exec) >= self.aggregation_count:
                mn, md, mx = min_median_max(self.exec)
                del self.exec[:]
                self.statsd.timing('msg.exec', md, tags=self.tags)

        def append_erro(self, delta):
            self.erro.append(delta)
            if len(self.erro) >= self.aggregation_count:
                mn, md, mx = min_median_max(self.erro)
                del self.erro[:]
                self.statsd.timing('msg.erro', md, tags=self.tags)

        def append_wait(self, delta):
            self.wait.append(delta)
            if len(self.wait) >= self.aggregation_count:
                mn, md, mx = min_median_max(self.wait)
                del self.wait[:]
                self.statsd.timing('msg.wait', md, tags=self.tags)


except ImportError:

    class Statsd(Base):
        def __init__(self, aggregation_count, tags=None, **kwargs):
            super(Statsd, self).__init__(aggregation_count)
            _log.warning('Statsd time_reporter unavailable, using noop. (Do you need to "pip install statsdecor"?)')
