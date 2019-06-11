from .request import request
from . import validator

__all__ = ['Subscription', ]


class Subscription:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def get_subscription_json(self, address, offset=0, limit=10):
        """
        :param address: str,
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path=f'/users/{address}/subscription.json',
            query=query,
            headers={'Content-Type': 'application/json'},
            debug=self.config.debug,
        )

    def get_subscriptions(self, address, offset=0, limit=10):
        """
        :param address: str,
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path=f'/users/{address}/subscription',
            query=query,
            debug=self.config.debug,
        )

    def get_subscribers(self, address, offset=0, limit=10):
        """
        :param address: str,
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path=f'/users/{address}/subscribers',
            query=query,
            debug=self.config.debug,
        )

    def get_recommendation_json(self, offset=0, limit=10):
        """
        :param address: str,
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path='feeds/recommendation.json',
            query=query,
            headers={'Content-Type': 'application/json'},
            debug=self.config.debug,
        )

    def get_recommendations(self, offset=0, limit=10):
        """
        :param address: str,
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path='feeds/recommendation',
            query=query,
            headers={'Content-Type': 'application/json'},
            debug=self.config.debug,
        )

    def subscribe(self, address):
        """
        :param address: str,
        """
        data = {'subscription_address': address}
        return request(
            self.config.host,
            method='POST',
            path=f'/subscription/{address}',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def unsubscribe(self, address):
        """
        :param address: str,
        """
        data = {'subscription_address': address}
        return request(
            self.config.host,
            method='DELETE',
            path=f'/subscription/{address}',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def check_subscription(self, subscriber_address, publisher_address):
        """
        :param subscriber_address: str
        :param publisher_address: str
        """
        path = f'/users/{subscriber_address}/subscription/{publisher_address}'
        return request(
            self.config.host,
            method='GET',
            path=path,
            debug=self.config.debug,
        )
