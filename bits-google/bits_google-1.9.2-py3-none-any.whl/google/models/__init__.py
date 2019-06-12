"""Google Models class file."""

from .billing_account import BillingAccount
from .invoice import Invoice


class Models(object):
    """Google Models class."""

    def __init__(self, google=None):
        """Initialize a Google Models instance."""
        self.google = google

    def billing_account(self):
        """Return a Google Billing Account instance."""
        return BillingAccount(self.google)

    def invoice(self):
        """Return a Google Invoice instance."""
        return Invoice(self.google)
