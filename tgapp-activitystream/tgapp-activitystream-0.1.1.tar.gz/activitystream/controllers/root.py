# -*- coding: utf-8 -*-
"""Main Controller"""
from datetime import datetime
from tg import TGController, expose, request, redirect
from tg.predicates import not_anonymous


class RootController(TGController):
    allow_only = not_anonymous()

    @expose('json')
    def ajax_update_last_seen_of_a_recipient(self):
        result = {'last_activity_seen': request.identity['user'].last_activity_seen}
        request.identity['user'].last_activity_seen = datetime.utcnow()
        return result

    @expose()
    def see(self, target_link):
        request.identity['user'].last_activity_seen = datetime.utcnow()
        return redirect(target_link)
