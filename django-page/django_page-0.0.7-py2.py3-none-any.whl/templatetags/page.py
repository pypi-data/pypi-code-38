# -*- coding: utf-8 -*-
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

import os

from page.models import Page, Pagelet, DownloadableFile
from page.shortcode import unpack_content_with_request

register = template.Library()


@register.simple_tag(takes_context=True)
def page(context, page_code):
    if not page_code:
        return ""

    page_obj, _ = Page.objects.get_or_create(code=page_code, defaults={'title': page_code, 'content': page_code})
    return unpack_content_with_request(context['request'], page_obj.content, {
        'title': page_obj.title,
        'edit': reverse('admin:page_page_change', args=[page_obj.id])
    })


@register.simple_tag(takes_context=True)
def pagelet(context, pagelet_code):
    if not pagelet_code:
        return ""

    try:
        pagelet_obj = Pagelet.objects.get(title=pagelet_code)
    except Pagelet.DoesNotExist:
        pagelet_obj, _ = Pagelet.objects.get_or_create(code=pagelet_code,
                                                       defaults={'title': pagelet_code, 'content': pagelet_code})

    return unpack_content_with_request(context['request'], pagelet_obj.content, {
        'title': pagelet_obj.title,
        'edit': reverse('admin:page_page_change', args=[pagelet_obj.id])
    })


@register.simple_tag(takes_context=True)
def pagelet_title(context, pagelet_code):
    if not pagelet_code:
        return ""

    try:
        pagelet_obj = Pagelet.objects.get(title=pagelet_code)
    except Pagelet.DoesNotExist:
        pagelet_obj, _ = Pagelet.objects.get_or_create(code=pagelet_code,
                                                       defaults={'title': pagelet_code, 'content': pagelet_code})

    return pagelet_obj.title


@register.simple_tag
def download(value, color='button-border white'):
    try:
        int_value = int(value)
        target = DownloadableFile.objects.get(pk=int_value)
    except (ValueError, DownloadableFile.DoesNotExist):
        target = None

    if not target:
        try:
            target = DownloadableFile.objects.get(name=value)
        except DownloadableFile.DoesNotExist:
            return ""

    if not target.file:
        return mark_safe("""<a class="button %s" href="#" 
            data-toggle="modal" data-target="#error-dialog" data-message="죄송합니다! %s 다운로드가 아직 준비되지 않았습니다."> 
            <span> %s 다운받기</span>
            <i class="fa fa-download"></i>
            </a>""" % (color, target.name, target.name))

    url = reverse("page:download", args=(target.pk,)) + os.path.basename(target.file.name)

    return mark_safe("""<a class="button %s" href="%s">
                        <span>%s 다운받기</span>
                        <i class="fa fa-download"></i>
                    </a>""" % (color ,url, target.name))


@register.simple_tag
def view(value):
    try:
        int_value = int(value)
        target = DownloadableFile.objects.get(pk=int_value)
    except (ValueError, DownloadableFile.DoesNotExist):
        target = None

    if not target:
        try:
            target = DownloadableFile.objects.get(name=value)
        except DownloadableFile.DoesNotExist:
            return ""

    return mark_safe(
        '<a class="btn btn-primary" href="%s"><i class="fa fa-eye"></i> "%s" 보기</a>' % (target.file.url, target.name))
