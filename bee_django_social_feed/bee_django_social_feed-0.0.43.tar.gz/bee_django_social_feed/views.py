# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from bee_django_social_feed.models import Feed, FeedComment, FeedImage, AlbumPhoto, Album, FeedStickSettings
# from django.core.serializers import serialize
from dss.Serializer import serializer
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from bee_django_social_feed.exports import get_classmates, get_feed_user_name_field
from bee_django_social_feed import signals
from django.db import transaction
from django.db.models import Q
import pytz

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

user_model = get_user_model()

def page_it(request, query_set, url_param_name='page', items_per_page=25):
    paginator = Paginator(query_set, items_per_page)

    page = request.GET.get(url_param_name)
    try:
        rs = paginator.page(page)
    except PageNotAnInteger:
        rs = paginator.page(1)
    except EmptyPage:
        rs = paginator.page(paginator.num_pages)

    return rs


def index(request):
    return render(request, 'bee_django_social_feed/index.html', context={
    })


# 获取所有日志
def feeds(request):
    page = request.GET.get('page')
    keywords = request.GET.get('search_keywords')
    # 依据type的值，判断是取所有日志，还是单个用户的日志，或者同班同学的，或者单个日志
    tp = request.GET.get('type')

    # 如果有置顶日志，检查时间失效与否
    stick_feeds = Feed.objects.filter(is_stick=True)
    now = timezone.now()
    for e in stick_feeds:
        if e.stick_expired_at and e.stick_expired_at <= now:
            e.is_stick = False
            # 失效的置顶 则变为正常
            e.save()

    if tp == '0':
        feeds_data = Feed.objects.order_by('-is_stick', '-created_at')
    elif tp == '1':
        user_id = request.GET.get('user_id')
        user = get_object_or_404(user_model, pk=user_id)
        feeds_data = Feed.objects.filter(publisher=user).order_by('-is_stick', '-created_at')
    elif tp == '2':
        user_id = request.GET.get('user_id')
        classmates = get_classmates(user_id)
        feeds_data = Feed.objects.filter(publisher__in=classmates).order_by('-is_stick', '-created_at')
    elif tp == '3':
        feed_id = request.GET.get('display_id')
        feeds_data = Feed.objects.filter(id=feed_id)
    elif tp == '4':
        feeds_data = Feed.objects.filter(is_star=True).order_by('-is_stick', '-created_at')
    else:
        feeds_data = Feed.objects.order_by('-is_stick', '-created_at')

    if keywords:
        kwargs = {}
        user_name_field = get_feed_user_name_field()
        kwargs[user_name_field + '__contains'] = keywords
        feeds_data = feeds_data.filter(Q(content__contains=keywords) | Q(**kwargs))

    paginator = Paginator(feeds_data, 10)
    try:
        data = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        data = []

    for e in data:
        e.emojis = e.feedemoji_set.all()
        for i in e.emojis:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
            i.user_name = user_model.objects.get(pk=i.user_id).get_user_name()
            i.user_avatar = unicode(user_model.objects.get(pk=i.user_id).get_user_profile_image())
        e.comments = e.feedcomment_set.order_by('created_at')
        for j in e.comments:
            j.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=j.user_id)
            j.user_name = user_model.objects.get(pk=j.user_id).get_user_name()
            j.user_avatar = unicode(user_model.objects.get(pk=j.user_id).get_user_profile_image())
            if j.to_user:
                j.to_user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=j.to_user.id)
                j.to_user_name = user_model.objects.get(pk=j.to_user.id).get_user_name()
                # j.user_avatar = unicode(user_model.objects.get(pk=j.to_user.id).get_user_profile_image())
        e.publisher_data = user_model.objects.values('id', 'username', 'first_name').get(pk=e.publisher_id)
        e.publisher_name = user_model.objects.get(pk=e.publisher_id).get_user_name()
        e.publisher_avatar = unicode(user_model.objects.get(pk=e.publisher_id).get_user_profile_image())
        e.publisher_icon_list = e.publisher_icon_list()


        if e.type == 0:
            e.images = e.feedimage_set.all()
        elif e.type == 1:
            if e.check_link_link(request.user, e.type_id):
                pass
            else:
                e.link_link = None
        elif e.type == 2:
            if e.album:
                e.images = e.album.albumphoto_set.all()
            else:
                e.images = []
        else:
            e.images = []

    feeds = serializer(data, output_type='json', datetime_format='string')
    return JsonResponse(data={
        # 'feeds': serializer(data, output_type='json', datetime_format='string'),
        'feeds': feeds,
        'page': page,
        'request_user_id': request.user.id,
        'can_manage': request.user.has_perm('bee_django_social_feed.can_manage_feeds'),
        'can_delete': request.user.has_perm('bee_django_social_feed.delete_feed'),
    })


# 发表日志
@transaction.atomic
def create_feed(request):
    if request.method == "POST":
        # 日志每天只能发3篇
        today = timezone.now().date()
        tz = pytz.timezone('Asia/Shanghai')
        today_start = datetime(today.year, today.month, today.day, tzinfo=tz)
        today_end = today_start + timedelta(hours=24)
        feeds_of_today = Feed.objects.filter(publisher=request.user, type=0,
                                             created_at__gte=today_start, created_at__lt=today_end)
        if feeds_of_today.count() >= 3:
            return JsonResponse(data={
                'rc': -1,
                'message': '发表失败！每天只能发3篇',
                'new_feeds': []
            })

        content = request.POST.get('content')
        user_stick_settings = FeedStickSettings.objects.filter(user=request.user)
        if user_stick_settings.exists():
            stick_setting = user_stick_settings.first()
            date_expired = datetime.now() + timedelta(days=stick_setting.duration)
            new_feed = Feed.objects.create(content=content, publisher=request.user,
                                           is_stick=True, stick_expired_at=date_expired)
        else:
            new_feed = Feed.objects.create(content=content, publisher=request.user)

        for i in request.FILES.getlist('files'):
            image = FeedImage.objects.create(image=i, feed=new_feed)

        new_feed.emojis = []
        new_feed.comments = []
        new_feed.publisher_data = user_model.objects.values('id', 'username', 'first_name').get(
            pk=new_feed.publisher_id)
        new_feed.publisher_name = user_model.objects.get(pk=new_feed.publisher_id).get_user_name()
        new_feed.publisher_avatar = unicode(user_model.objects.get(pk=new_feed.publisher_id).get_user_profile_image())
        new_feed.publisher_icon_list = new_feed.publisher_icon_list()
        new_feed.images = new_feed.feedimage_set.all()

        # 发送发表日志的信号
        signals.user_feed_created.send(sender=Feed, feed_id=new_feed.id)

        new_feed = serializer(new_feed, output_type='json', datetime_format='string')

        return JsonResponse(data={
            'rc': 0,
            'message': '发表成功',
            'new_feeds': new_feed
        })


# 删除日志
def delete_feed(request, feed_id):
    feed = get_object_or_404(Feed, pk=feed_id)
    if request.method == "POST":
        if request.user.has_perm('bee_django_social_feed.delete_feed') or request.user == feed.publisher:
            signals.user_feed_delete.send(sender=Feed, feed_publisher=feed.publisher, feed_type=feed.type)

            feed.delete()
            return JsonResponse(data={
                'rc': 0,
                'message': '删除成功'
            })
        else:
            return JsonResponse(data={
                'rc': -1,
                'message': '权限不足'
            })


# 删除日志评论
def delete_feed_comment(request, feed_comment_id):
    comment = get_object_or_404(FeedComment, pk=feed_comment_id)
    if request.method == "POST":
        if request.user.has_perm('bee_django_social_feed.can_manage_feeds') or request.user == comment.user:
            comment.delete()
            return JsonResponse(data={
                'rc': 0,
                'message': '删除成功'
            })
        else:
            return JsonResponse(data={
                'rc': -1,
                'message': '权限不足'
            })


# 点赞
def create_emoji(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)

        # 检查用户是否已经点过赞了
        emojis = feed.feedemoji_set.filter(user=request.user)
        if emojis.exists():
            message = '你已经点过赞了'
            new_emoji = None
        else:
            new_emoji = feed.feedemoji_set.create(user=request.user)
            signals.user_feed_emojied.send(sender=Feed, feed_id=feed.id, emojier=request.user)
            message = '点赞成功'

        emojis = [new_emoji, ]
        for i in emojis:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
            i.user_name = user_model.objects.get(pk=i.user_id).get_user_name()
            i.user_avatar = unicode(user_model.objects.get(pk=i.user_id).get_user_profile_image())
        return JsonResponse(data={
            'message': message,
            'new_emoji': serializer(emojis, output_type='json', datetime_format='string')
        })


# 发表对日志的评论
def create_comment(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)

        comment_text = request.POST.get('comment')
        to_user_id = request.POST.get('to_user_id')
        if to_user_id:
            to_user = get_object_or_404(user_model, pk=to_user_id)
        else:
            to_user = None
        new_comment = feed.feedcomment_set.create(comment=comment_text, user=request.user, to_user=to_user)
        message = '评论成功'
        signals.user_feed_replied.send(sender=Feed, feed_id=feed.id, replier=request.user)
        if to_user:
            signals.user_feedcomment_replied.send(sender=Feed, feedcomment_id=new_comment.id, replier=request.user)

        comments = [new_comment, ]
        for i in comments:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
            i.user_avatar = unicode(user_model.objects.get(pk=i.user_id).get_user_profile_image())
            i.user_name = user_model.objects.get(pk=i.user_id).get_user_name()
            if i.to_user:
                i.to_user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.to_user_id)
                i.to_user_name = user_model.objects.get(pk=i.to_user_id).get_user_name()
        return JsonResponse(data={
            'message': message,
            'new_comments': serializer(comments, output_type='json', datetime_format='string')
        })


# 把日志加为精华
def star_feed(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)

        if feed.star_at:
            # 有加精时间，所以不是第一次加精
            signals.user_feed_star.send(sender=Feed, feed=feed, first_star=False)
        else:
            signals.user_feed_star.send(sender=Feed, feed=feed, first_star=True)

        feed.is_star = True
        feed.star_by = request.user
        feed.star_at = timezone.now()
        feed.save()

        return JsonResponse(data={
            'message': '加精成功'
        })


def unstar_feed(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)
        if feed.is_star:
            feed.is_star = False
            feed.star_by = None
            feed.star_at = None
            feed.save()

        signals.user_feed_unstar.send(sender=Feed, feed=feed)

        return JsonResponse(data={
            'message': '取消加精成功'
        })


# 日志置顶
def stick_feed(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)
        feed.is_stick = True
        feed.stick_expired_at = None
        feed.save()

        return JsonResponse(data={
            'message': '置顶成功'
        })


# 取消置顶
def unstick_feed(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)
        if feed.is_stick:
            feed.is_stick = False
            feed.stick_expired_at = None
            feed.save()

        return JsonResponse(data={
            'message': '取消置顶成功'
        })


# 美好的生活页面 显示所有用户的albums的页面
def albums(request):
    return render(request, 'bee_django_social_feed/albums.html', context={
        'user_id': request.user.id,
    })


# 获取albums实际数据
def get_albums(request):
    page = request.GET.get('page')
    # 自己的显示所有，别人的只显示审核通过的
    albums = Album.objects.filter((Q(status__in=[1, 2]) & ~Q(user=request.user)) | Q(user=request.user))

    paginator = Paginator(albums, 25)
    try:
        data = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        data = []

    for e in data:
        e.cover_image = e.albumphoto_set.first().thumbnail_url
        e.user_name = e.user.first_name or e.user.username

    data_albums = serializer(data, output_type='json', datetime_format='string')

    return JsonResponse(data={
        'albums': data_albums,
        'page': page,
    })


# 获取相册详情
def album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)

    album.photos = album.albumphoto_set.all()
    album.user_name = album.user.first_name or album.user.username

    data_album = serializer(album, output_type='json', datetime_format='string')

    return JsonResponse(data={
        'album': data_album,
    })


# 创建相册
@transaction.atomic
def create_album(request):
    if request.method == "POST":
        # 每天只能发1篇
        today = timezone.now().date()
        tz = pytz.timezone('Asia/Shanghai')
        today_start = datetime(today.year, today.month, today.day, tzinfo=tz)
        today_end = today_start + timedelta(hours=24)
        count_of_today = Album.objects.filter(user=request.user,
                                              created_at__gte=today_start, created_at__lt=today_end).count()
        if count_of_today >= 1:
            return JsonResponse(data={
                'rc': -1,
                'message': '发表失败！每天只能发1篇',
                'albums': [],
            })

        file_list = request.FILES.getlist('files')
        if not file_list:
            return JsonResponse(data={
                'rc': -1,
                'albums': [],
                'message': '上传图片不能为空',
            })

        note = request.POST.get('note')
        new_album = Album.objects.create(user=request.user, note=note)

        for i in request.FILES.getlist('files'):
            image = AlbumPhoto.objects.create(image=i, album=new_album)

        # 构造其他需要的数据
        new_album.cover_image = new_album.albumphoto_set.first().thumbnail_url
        new_album.user_name = request.user.first_name or request.user.username

        new_albums = [new_album, ]
        data_albums = serializer(new_albums, output_type='json', datetime_format='string')

        return JsonResponse(data={
            'rc': 0,
            'albums': data_albums,
            'message': '上传成功',
        })


# 管理上传的美好生活
def manage_albums(request):
    type = request.GET.get('type')

    if type == 'finished':
        album_list = Album.objects.filter(~Q(status=0))
    else:
        album_list = Album.objects.filter(status=0)

    data = page_it(request, query_set=album_list)
    return render(request, 'bee_django_social_feed/manage_albums.html', context={
        'albums': data,
        'type': type,
    })


# 管理查看单个相册，并评分
@transaction.atomic
def manage_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)

    if request.method == "POST":
        level = request.POST.get('level')
        print request.POST
        if level == "1":
            album.status = 1
            message = '审核成功'
            album.create_feed()
        elif level == "2":
            album.status = 2
            message = '审核成功'
            album.create_feed()
        elif level == "3":
            album.status = 3
            message = '阻止成功'
        else:
            message = '未知评分类型'

        album.save()
        # 美好生活审核后的信号
        signals.user_album_checked.send(sender=Album, album_id=album.id)
        return JsonResponse(data={
            'message': message,
        })
    else:
        return render(request, 'bee_django_social_feed/manage_album.html', context={
            'album': album,
        })


# 修改图片的描述
def update_album_photo_note(request, album_photo_id):
    if request.method == "POST":
        album_photo = get_object_or_404(AlbumPhoto, pk=album_photo_id)
        new_note = request.POST.get('note')
        album_photo.note = new_note
        album_photo.save()

        return JsonResponse(data={
            'message': '修改成功',
        })
