# -*- coding: utf-8 -*-

'''
Created on 2014-5-18
@author: linkeddt.com
'''

from __future__ import unicode_literals

from django.views.generic import TemplateView


def _get_page_url(query):
    """
    通过获取query中GET的url字段获取iframe的src值，但是要处理一下情况
    url=http://ip:9002/api/microapp_token/connect/?appid=video&redirect_uri=http://ip:9004/video/video_monitoring/
    应该将url后的值当成一个整体。
    """
    q = query.dict()

    url = q.get('url', '')
    del q['url']

    _arr = []
    for k, v in q.items():
        _arr.append('&%s=%s' % (k, v))
    page_url = url + ''.join(_arr)
    return page_url


class IframeView(TemplateView):
    template_name = "admin/iframe.htm"

    def get(self, request, *args, **kwargs):
        context = super(IframeView, self).get_context_data(**kwargs)
        query = self.request.GET.copy()
        page_url = _get_page_url(query)
        context['page_url'] = page_url
        return self.render_to_response(context)


class IframeScrollView(TemplateView):
    template_name = "admin/iframe_scroll.htm"

    def get(self, request, *args, **kwargs):
        context = super(IframeScrollView, self).get_context_data(**kwargs)
        query = self.request.GET.copy()
        page_url = _get_page_url(query)
        context['page_url'] = page_url
        return self.render_to_response(context)
