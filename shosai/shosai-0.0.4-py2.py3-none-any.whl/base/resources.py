import logging


class LoggedRequestMixin:
    logger = logging.getLogger(__name__)

    def request(self, method, url, params=None, *args, **kwargs):
        if params is not None:
            self.logger.info("%s %s, params=%s", method, url, params)
        else:
            self.logger.info("%s %s", method, url)
        response = super().request(method, url, *args, params=params, **kwargs)
        self.logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response
