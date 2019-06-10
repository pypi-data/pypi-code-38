from . import APIBase
from ..exceptions import MissingFieldException


# https://www.giftbit.com/giftbitapi/#/reference/1/campaign
class CampaignMixin(APIBase):
  def create_campaign(
      self,
      contacts,
      price_in_cents,
      brand_codes,
      campaign_id,
      expiry=None,
      message=None,
      subject=None,
      gift_template=None,
  ):
    if not ((message and subject) or gift_template):
      raise MissingFieldException('If not providing gift_template, both message and subject must be set')

    json = {
      'contacts': contacts,
      'price_in_cents': price_in_cents,
      'brand_codes': brand_codes,
      'id': campaign_id,
    }

    if message and subject:
      json['message'] = message
      json['subject'] = subject

    if gift_template:
      json['gift_template'] = gift_template

    if expiry:
      json['expiry'] = expiry

    return self.post(
      'campaign',
      json=json,
    )

  def retrieve_campaign(self, campaign_id):
    return self.get(f'campaign/{campaign_id}')
