from pyqalx.core.errors import QalxError


class QalxSignal(object):
    """
    A set of helper methods to aid in managing signals on Bots and Workers
    """
    BASE_EXIT_CODE = 72590
    TERMINATE_WARM_CODE = 72591
    TERMINATE_COLD_CODE = 72592
    CONFIG_TERMINATE_CODE = 72593
    COLD_EXIT_KEY = 'cold'
    WARM_EXIT_KEY = 'warm'
    REQUEUE_JOB_KEY = 'requeue_job'
    STOP_KEY = 'stop'
    TERMINATE_KEY = 'terminate'

    def __init__(self, entity):
        self.signal = entity['signal']

    @classmethod
    def _build_signal(cls, key, value):
        """
        Builds the signal structure.  A signal should be a dict in the format
        {<key>: <bool>}
        """
        return {key: value}

    @classmethod
    def _terminate_signal(cls):
        return cls._build_signal(cls.TERMINATE_KEY, True)

    @classmethod
    def _terminate_warm_signal(cls):
        return cls._build_signal(cls.WARM_EXIT_KEY, True)

    @classmethod
    def _stop_signal(cls, stop):
        return cls._build_signal(cls.STOP_KEY, stop)

    @classmethod
    def _build_update(cls, update, code):
        """
        Builds an update to publish to the worker/bot status

        :param update: The update string
        :param code: The exist code
        """
        return {'update': update, 'code': code}

    @classmethod
    def _bot_triggered_exit_update(cls):
        return cls._build_update('bot triggered', cls.TERMINATE_WARM_CODE)

    @classmethod
    def _warm_exit_update(cls):
        return cls._build_update(f'{cls.WARM_EXIT_KEY} exit signal found',
                                 cls.TERMINATE_WARM_CODE)

    @classmethod
    def _cold_exit_update(cls):
        return cls._build_update(f'{cls.COLD_EXIT_KEY} exit signal found',
                                 cls.TERMINATE_COLD_CODE)

    @property
    def terminate(self):
        """
        Checks whether the signal was a terminate signal
        """
        return self.signal.get(self.TERMINATE_KEY)

    @property
    def terminate_cold(self):
        """
        Checks whether the signal was a cold terminate signal
        """
        return bool(self.terminate and self.signal.get(self.COLD_EXIT_KEY))

    @property
    def terminate_warm(self):
        """
        Checks whether the signal was a warm terminate signal
        """
        return bool(self.terminate and self.signal.get(self.WARM_EXIT_KEY))

    @property
    def requeue_job(self):
        """
        Checks whether the signal wants the job to be requeued
        """
        return bool(self.signal.get(self.REQUEUE_JOB_KEY))

    @property
    def stop(self):
        """
        Checks whether the signal wants to stop the job
        """
        return bool(self.signal.get(self.STOP_KEY))


class QalxBotSignal(QalxSignal):
    """
    signals for bots.
    """

    @classmethod
    def _terminate_signal(cls):
        """
        Bots can only warm terminate
        """
        signal = super(QalxBotSignal, cls)._terminate_signal()
        warm = cls._terminate_warm_signal()
        return {**signal, **warm}


class QalxWorkerSignal(QalxSignal):
    @classmethod
    def _terminate_cold_signal(cls, requeue_job):
        cold = cls._build_signal(cls.COLD_EXIT_KEY, True)
        requeue = cls._build_signal(cls.REQUEUE_JOB_KEY, bool(requeue_job))
        return {**requeue, **cold}

    @classmethod
    def _terminate_signal(cls, warm=True, requeue_job=None, **kwargs):
        """
        Workers can either warm or cold terminate.

        :param warm: Whether this should be a warm or cold termination
        :param requeue_job: Whether we should requeue the job (cold terminate
                            only)
        :param kwargs:
        :return:
        """
        signal = super(QalxWorkerSignal, cls)._terminate_signal()
        if warm and requeue_job:
            raise QalxError(
                "warm termination cannot be called with requeue_job, you "
                "need to add the job to the queue manually.")
        if warm:
            extra = cls._terminate_warm_signal()
        else:
            extra = cls._terminate_cold_signal(requeue_job=requeue_job)
        return {**signal, **extra}

