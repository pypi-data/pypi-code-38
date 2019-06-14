__author__ = 'bee'

from .models import Feed


def get_user_feed(user, start_dt=None, end_dt=None):
    feed_list = Feed.objects.filter(publisher=user)
    if start_dt:
        feed_list = feed_list.filter(created_at__gte=start_dt)
    if end_dt:
        feed_list = feed_list.filter(created_at__lte=start_dt)
    return feed_list
