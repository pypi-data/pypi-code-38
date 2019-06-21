from .base import TelegramEndpoint
from .commons import DisableNotification, ReplyToMessageId
from .reply_markup import ReplyMarkup


class SendVenue(TelegramEndpoint, DisableNotification, ReplyMarkup, ReplyToMessageId):
    def __init__(self, chat_id, latitude, longitude, title, address):
        args = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'title': title,
            'address': address  # noqa: S001
        }
        super().__init__(args=args)

    def foursquare_id(self, foursquare_id):
        self.args['foursquare_id'] = foursquare_id
        return self

    def foursquare_type(self, foursquare_type):
        self.args['foursquare_type'] = foursquare_type
        return self
