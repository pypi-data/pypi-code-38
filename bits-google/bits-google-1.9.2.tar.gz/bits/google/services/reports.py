"""Google admin reports SDK."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Reports(Base):
    """Google Admin Reports class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.admin = build('admin', 'reports_v1', credentials=credentials)

    def get_activities(self, user, app):
        """Return list of user activities."""
        params = {
            'userKey': user,
            'applicationName': app,
        }
        activities = self.admin.activities()
        request = activities.list(**params)
        return self.get_list_items(activities, request, 'items')

    def get_customer_reports(self, date, parameters=None):
        """Return list of customer usage reports."""
        params = {
            'date': date,
            'parameters': parameters,
        }
        usage_reports = self.admin.customerUsageReports()
        request = usage_reports.get(**params)

        google_usage_reports = []

        while request is not None:
            usage_reports_list = request.execute()

            for w in usage_reports_list.get('warnings', []):
                print('%s: %s' % (w['code'], w['message']))

            google_usage_reports += usage_reports_list.get('usageReports', [])
            request = usage_reports.get_next(request, usage_reports_list)

        return google_usage_reports

    def get_user_reports(self, user, date, parameters=None):
        """Return list of user usage reports."""
        params = {
            'date': date,
            'userKey': user,
            'parameters': parameters,
        }
        usage_reports = self.admin.userUsageReport()
        request = usage_reports.get(**params)

        google_usage_reports = []

        while request is not None:
            usage_reports_list = request.execute()
            google_usage_reports += usage_reports_list.get('usageReports', [])
            request = usage_reports.get_next(request, usage_reports_list)

        return google_usage_reports
