from .base import TelegramEndpoint
from .exceptions import InvalidUpdateType


class SetWebhook(TelegramEndpoint):
    update_types = [
        'message', 'edited_message', 'channel_post', 'edited_channel_post', 'inline_query', 'chosen_inline_result',
        'callback_query', 'shipping_query', 'pre_checkout_query'
    ]

    def __init__(self, url):
        args = {
            'url': url
        }
        super().__init__(args=args)

    def certificate(self, certificate):
        self.args['certificate'] = certificate
        return self

    def max_connections(self, max_connections):
        self.args['max_connections'] = max_connections
        return self

    def allowed_updates(self, allowed_updates):
        for update_type in allowed_updates:
            if update_type not in self.update_types:
                raise InvalidUpdateType

        self.args['allowed_updates'] = allowed_updates
        return self


class DeleteWebhook(TelegramEndpoint):
    pass


class GetWebhookInfo(TelegramEndpoint):
    pass
