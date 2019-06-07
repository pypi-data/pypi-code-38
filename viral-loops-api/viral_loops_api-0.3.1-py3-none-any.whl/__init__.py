from viral_loops_api.api.altruistic_referral import AltruisticReferralMixin
from viral_loops_api.api.utils import UtilsMixin


# Everything we need is available from the mixins, and separated by
# which segment of documentation they were converted from
class API(AltruisticReferralMixin, UtilsMixin):
  pass
