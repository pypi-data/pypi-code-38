from .request import request
from . import validator

__all__ = ['Block', ]


class Block:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def get_by_rids(self, rids, with_detail=False):
        """
        :param rids: list
        :param with_detail: bool, default value: False
        """
        validator.assert_exc(rids, 'rids cannot be null')
        ids = ','.join(rids)
        query = {'withDetail': 'true'} if with_detail is True else None
        return request(
            self.config.host,
            method='GET',
            path=f'/blocks/{ids}',
            query=query,
            debug=self.config.debug,
        )
