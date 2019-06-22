"""
Module where admin tools dashboard modules classes are defined.
"""

# Basic dashboard module from django admin tools
from admin_tools.dashboard.modules import DashboardModule

# Functions to get data from goole analytics
from admin_tools_google_analytics.googleapi import get_visitors, get_visitors_total


def formate_dates(children):
    dates = children['dates']
    new_dates = []
    for date in dates:
        new_dates.append('{}/{}'.format(str(date)[4:6], str(date)[6:8]))
    children['dates'] = new_dates
    print(new_dates)
    return children


class GoogleVisitorsChart(DashboardModule):

    title = 'google analytics visitors chart'
    template = 'admin_tools_google_analytics/visitors_chart.html'
    color = "#1F5068"
    formate_fn = formate_dates

    def init_with_context(self, context):
        if self._initialized:
            return

        children = get_visitors()

        self.children = formate_dates(children)
        self._initialized = True

class GoogleVisitorsTotal(DashboardModule):

    title = 'google analytics visitors total'
    template = 'admin_tools_google_analytics/visitors_total.html'

    def init_with_context(self, context):
        if self._initialized:
            return
        
        children = get_visitors_total()