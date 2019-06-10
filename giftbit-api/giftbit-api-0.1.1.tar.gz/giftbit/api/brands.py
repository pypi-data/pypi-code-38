from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/0/brands
class BrandsMixin(APIBase):
  def list_brands(
      self,
      region=None,
      max_price_in_cents=None,
      min_price_in_cents=None,
      currency_iso_code=None,
      search=None,
      limit=20,
      offset=0,
      embeddable=False,
  ):
    params = {
      'limit': limit,
      'offset': offset,
    }

    if region:
      params['region'] = region

    if max_price_in_cents:
      params['max_price_in_cents'] = max_price_in_cents

    if min_price_in_cents:
      params['min_price_in_cents'] = min_price_in_cents

    if currency_iso_code:
      params['currencyisocode'] = currency_iso_code

    if search:
      params['search'] = search

    if embeddable:
      params['embeddable'] = embeddable

    return self.get('brands', params=params)

  def retrieve_brand(self, brand_code):
    return self.get(f'brands/brand_code')
