from .altruistic_referral import AltruisticReferralMixin
from .utils_mixin import UtilsMixin


# Everything we need is available from the mixins, and separated by
# which segment of documentation they were converted from
class API(AltruisticReferralMixin, UtilsMixin):
  pass
