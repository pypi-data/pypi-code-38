import time
from threading import Lock, RLock, Timer
import logging

from akeyless_auth_api import SystemUserCredentialsReplyObj
from akeyless.auth import Authenticator
from akeyless.auth import RenewalMode
from akeyless.exceptions import CredsRenewalError


_LOGGER = logging.getLogger(__name__)


class CredsRenewal(object):
    _renewal_latency = 60 * 30  # The amount of time before expiry to start the credentials renewal in seconds.
    _creds_threshold = 60  # The amount of time before expiry to stop using the credentials in seconds.

    def __init__(self, authenticator, mode=RenewalMode.LAZY):
        # type: (Authenticator, RenewalMode) -> None
        self.closed = False
        self._authenticator = authenticator
        self._mode = mode
        self._renewal_task = None
        self._creds = SystemUserCredentialsReplyObj(expiry=0)

        self._renewal_task_lock = Lock()
        self._creds_lock = RLock()

        self._init_scheduler()

    def get_auth_creds(self):
        # type: () -> str
        self._validate()
        with self._creds_lock:
            return self._creds.auth_creds

    def get_expiry(self):
        # type: () -> int
        self._validate()
        with self._creds_lock:
            return self._creds.expiry

    def get_kfm_creds(self):
        # type: () -> str
        self._validate()
        with self._creds_lock:
            return self._creds.kfm_creds

    def get_uam_creds(self):
        # type: () -> str
        self._validate()
        with self._creds_lock:
            return self._creds.uam_creds

    def close(self):
        # type: () -> None
        self.closed = True
        if self._renewal_task is not None and self._renewal_task.is_alive():
            self._renewal_task.cancel()

    def _init_scheduler(self):
        # type: () -> None
        if self._mode is RenewalMode.EAGER:
            self._renew_creds(True)
            next_renewal = max(self._creds.expiry - (int(time.time()) + self._renewal_latency), 1)
            self._schedule_renewal_task(next_renewal)
            _LOGGER.info("Credentials successfully renewed. Expires at: " + str(next_renewal))

    def _renew_creds(self, force=False):
        # type: (bool) -> None
        with self._creds_lock:
            if not force and self._is_not_expired():
                return

            _LOGGER.info("Starts renewing credentials")
            self._creds = self._authenticator.authenticate()

    def _validate(self):
        # type: () -> None
        if self._is_not_expired():
            return

        self._renew_creds(force=False)

        if self._mode is RenewalMode.EAGER and self._renewal_task is not None and not self._renewal_task.is_alive():
            # The task has been unexpectedly terminated, so restart it immediately
            _LOGGER.warning("Credentials renewal task has been unexpectedly terminated, restarts again")
            self._schedule_renewal_task(0)

    def _is_not_expired(self):
        return (self._creds.expiry - int(time.time())) >= self._creds_threshold

    def _renewer(self):
        # type: () -> None
        try:
            self._renew_creds(True)
            next_renewal = max(self._creds.expiry - (int(time.time()) + self._renewal_latency), 1)
            if not self.closed:
                self._schedule_renewal_task(next_renewal)
            _LOGGER.info("Credentials successfully renewed. Expires at: " + str(next_renewal))
        except CredsRenewalError as e:
            _LOGGER.error("Credentials renewal failed. Err:" + str(e))
            self._schedule_renewal_task(1)

    def _schedule_renewal_task(self, next_renewal):
        # type: (int) -> None
        with self._renewal_task_lock:
            lase_renewal_task = self._renewal_task
            self._renewal_task = Timer(next_renewal, self._renewer)
            self._renewal_task.start()
            if lase_renewal_task is not None and lase_renewal_task.is_alive():
                lase_renewal_task.cancel()
