from .base import APIBase
from .exceptions import MissingFieldException


class UtilsMixin(APIBase):
  def user_has_referrer(self, email=None, referral_code=None):
    if not (email or referral_code):
      raise MissingFieldException('Email or referral code required')

    result = self.get(
      'participant_data',
      body={
        'participants': [self.user_object(email, referral_code)],
      },
    )

    return 'email' in result['data'][0]['referrer']
