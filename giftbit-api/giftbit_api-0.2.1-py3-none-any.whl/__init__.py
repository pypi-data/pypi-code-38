from .api import *


class GiftbitClient(
    PingMixin,
    BrandsMixin,
    RegionsMixin,
    CampaignMixin,
    EmbeddedMixin,
    FundsMixin,
    GiftsMixin,
):
  pass
