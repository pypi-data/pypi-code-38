from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/1/embedded
class EmbeddedMixin(APIBase):
  def create_embedded_gift(self, price_in_cents, brand_code, campaign_id, contact=None):
    json = {
      'price_in_cents': price_in_cents,
      'brand_code': brand_code,
      'id': campaign_id,
    }

    if contact:
      json['contact'] = contact

    return self.post('embedded', json=json)
