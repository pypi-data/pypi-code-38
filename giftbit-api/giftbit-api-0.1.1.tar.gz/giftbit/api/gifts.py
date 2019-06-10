from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/1/gifts
class GiftsMixin(APIBase):
  def list_gifts(self, **kwargs):
    return self.get('gifts', params=kwargs)

  def retrieve_gift(self, uuid):
    return self.get(f'gifts/{uuid}')

  def resend_gift(self, uuid):
    return self.put(f'gifts/{uuid}', json={'resend': True})

  def cancel_gift(self, uuid):
    return self.delete(f'gifts/{uuid}')
