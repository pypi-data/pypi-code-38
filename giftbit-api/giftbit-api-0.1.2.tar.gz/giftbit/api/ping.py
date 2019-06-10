from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/0/ping/ping
class PingMixin(APIBase):
  def ping(self):
    return self.get('ping')
