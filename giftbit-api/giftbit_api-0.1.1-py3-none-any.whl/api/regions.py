from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/0/regions
class RegionsMixin(APIBase):
  def list_regions(self):
    return self.get('regions')
