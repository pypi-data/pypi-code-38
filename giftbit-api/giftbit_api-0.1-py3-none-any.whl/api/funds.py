from . import APIBase


# https://www.giftbit.com/giftbitapi/#/reference/1/funds
class FundsMixin(APIBase):
  def retrieve_funding_information(self):
    return self.get('funds')

  def add_funds(self, currency_iso_code, fund_amount_in_cents, event_id):
    return self.post(
      'funds',
      json={
        'currencyisocode': currency_iso_code,
        'fund_amount_in_cents': fund_amount_in_cents,
        'id': event_id,
      }
    )
