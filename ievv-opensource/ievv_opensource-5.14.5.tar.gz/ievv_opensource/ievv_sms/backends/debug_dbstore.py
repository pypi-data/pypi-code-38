from ievv_opensource.ievv_sms import sms_registry
from ievv_opensource.ievv_sms.models import DebugSmsMessage


class Backend(sms_registry.AbstractSmsBackend):
    """
    Backend that creates DebugSmsMessage object

    Useful for development.

    The backend_id for this backend is ``debug_dbstore``.
    """
    @classmethod
    def get_backend_id(cls):
        return 'debug_dbstore'

    def send(self):

        db_record = DebugSmsMessage()
        db_record.phone_number = self.phone_number
        db_record.message = self.message
        db_record.send_as = self.send_as or ''
        db_record.full_clean()
        db_record.save()
