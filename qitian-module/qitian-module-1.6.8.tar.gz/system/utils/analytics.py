from system.models import VisitLogs
from system.utils import tools


def track_visitor(request, flag=''):
    visit_log = VisitLogs()
    visit_log.user_agent = request.META.get('HTTP_USER_AGENT', '')
    visit_log.ip = tools.get_ip(request)
    visit_log.referrer = request.META.get('HTTP_REFERER', '')
    visit_log.url = request.get_full_path()
    visit_log.passport = flag
    visit_log.save()
    return visit_log
