from .base import APIBase
from .utils import validate_enum
from .exceptions import MissingFieldException, MissingReferrerException


# Converted from documentation at:
# https://intercom.help/viral-loops/the-altruistic-referral-template/the-altruistic-referral-your-web-app
class AltruisticReferralMixin(APIBase):
  def identify_user(
      self,
      first_name,
      last_name,
      email,
      referral_code=None,
      referral_email=None,
      referral_source=None,
  ):
    body = {
      'event': 'registration',
      'user': {
        'firstname': first_name,
        'lastname': last_name,
        'email': email,
      },
      'refSource': '',
    }

    if referral_code or referral_email:
      body['referrer'] = {}

    if referral_code:
      body['referrer']['referralCode'] = referral_code

    if referral_email:
      body['referrer']['email'] = referral_email

    if referral_source:
      body['refSource'] = validate_enum(
        referral_source,
        [
          'email',
          'facebook',
          'twitter',
          # This typo also appears in the docs
          'redit',
          'copy',
        ],
      )

    return self.post('events', body=body)

  def track_conversion(self, email):
    # Normally we would return this, but the API returns failure
    #   not with status code, but as a field in the response for this endpoint
    response = self.post(
      'events',
      body={
        'event': 'conversion',
        'user': {
          'email': email,
        },
      },
    )

    if response.get('status'):
      raise MissingReferrerException(f'{email} is missing a referrer')

    return response

  def get_pending_rewards(self, email=None, referral_code=None, limit=25, skip=0, paginate=False):
    body = {
      'filter': {
        'limit': limit,
        'skip': skip,
      },
    }

    if email or referral_code:
      body['user'] = self.user_object(email, referral_code)

    response = self.get(
      'pending_rewards',
      body=body,
      wrap=False,
    )

    result = response.get('pending')

    # There's some pretty arbitrary pagination rules on the api, so concatenate here
    if len(result) == limit and not paginate:
      return result + self.get_pending_rewards(
        email,
        referral_code,
        limit=limit,
        skip=skip + limit,
      )

    return result

  def redeem_reward(self, reward_id=None, email=None, referral_code=None):
    body = {}

    if not (reward_id or email or referral_code):
      raise MissingFieldException('No valid reward identifier given')

    if reward_id:
      body['rewardId'] = reward_id

    if email or referral_code:
      body['user'] = self.user_object(email, referral_code)

    return self.post(
      'rewarded',
      body=body,
      # In this specific request only, the API token is mixed in with the body
      wrap=False,
    )
