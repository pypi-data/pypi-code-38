# -*- coding: utf-8 -*-
import urllib

import re
import os
from django import template
from django.conf import settings

from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext, Context
from django.http import Http404, HttpResponse
from django.urls import reverse

from page.models import Page, DownloadableFile, Post, PostCategory

from django.core.exceptions import ObjectDoesNotExist

from page.shortcode import unpack_content_with_request


def page(request, page_id=None, page_code=None):

    if not page_id and not page_code:
        raise Http404("Page does not exist")

    page_obj = None

    try:
        if page_id:
            page_obj = Page.objects.get(pk=page_id)

        if page_code:
            page_obj = Page.objects.get(code=page_code)

    except ObjectDoesNotExist:
        raise Http404("Page does not exist")

    if not page_obj:
        raise Http404("Page does not exist")

    content = unpack_content_with_request(request, page_obj.content, {
        'title': page_obj.title,
        'edit': reverse('admin:page_page_change', args=[page_obj.id])
    })

    return render(request, 'page/page/page.html', {
        'page': page_obj,
        'content': content,
        'edit': reverse('admin:page_page_change', args=[page_obj.id]),
        'default_featured': settings.PAGE_FEATURED_DEFAULT if hasattr(settings, "PAGE_FEATURED_DEFAULT") else ''
        })


def post(request, post_id):
    if not post_id:
        raise Http404("Page does not exist")

    try:
        post_obj = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        post_obj = Post.objects.all().order_by('-created')[0]

    content = unpack_content_with_request(request, post_obj.content)

    return render(request, 'page/post/post.html', {
        'title': post_obj.title,
        'post': post_obj,
        'content': content,
        'cate': post_obj.cate,
        'edit': reverse('admin:page_post_change', args=[post_obj.id]),
        'default_featured': settings.PAGE_FEATURED_DEFAULT if hasattr(settings, "PAGE_FEATURED_DEFAULT") else ''
    })


def post_list(request, cate_id):
    cate = get_object_or_404(PostCategory, code=cate_id)
    posts = Post.objects.filter(active=True, cate=cate)

    default_selected = 0
    if posts:
        default_selected = posts[0].id

    try:
        selected = int(request.GET.get('id', default_selected))
    except ValueError:
        selected = default_selected

    return render(request, 'page/post/list.html', {
        'style_name': 'page/post/style/' + (cate.template or 'basic_list.html'),
        'cate': cate,
        'posts': posts,
        'selected': selected,
    })


def download(request, file_id):
    file_obj = get_object_or_404(DownloadableFile, pk=file_id)

    file_name = os.path.basename(file_obj.file.name)

    response = HttpResponse(file_obj.file, content_type='application/octet-stream')

    filename_header = 'filename*=UTF-8\'\'%s' % urllib.parse.quote(file_name.encode('utf-8'))
    response['Content-Disposition'] = 'attachment; ' + filename_header

    return response
