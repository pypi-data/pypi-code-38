# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import Truncator
from django.dispatch import receiver
from django.db.models.signals import post_save
from PIL import Image
import os
from django.template.defaultfilters import truncatewords

# Create your models here.

thumbnail_size = (128, 128)
thumbnail_crop_size = (0, 0, 128, 128)
medium_size = (480, 480)


# 创建一个小图片（thumbnail），和一个中等大小的图片
def resize_image(img_field):
    img = Image.open(img_field)

    medium_path = extend_name(img_field.path, 'medium')
    if medium_path:
        img.thumbnail(medium_size, Image.ANTIALIAS)
        img.save(medium_path)

    thumbnail_path = extend_name(img_field.path, 'thumbnail')
    if thumbnail_path:
        thumbnail = img.resize(thumbnail_size, Image.ANTIALIAS)
        thumbnail = thumbnail.crop(thumbnail_crop_size)
        thumbnail.save(thumbnail_path)


def resized_image_url(img_field, ext_name):
    image_url = img_field.url.split('/')
    image_name = os.path.basename(extend_name(img_field.path, ext_name))

    image_url.pop()
    image_url.append(image_name)

    return '/'.join(image_url)


def extend_name(file_path, ext_name):
    name_array = os.path.splitext(file_path)
    if len(name_array) != 2:
        return None

    return name_array[0] + "_" + ext_name + name_array[1]


class Feed(models.Model):
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='发布者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(default=timezone.now)
    # 0 普通日志，1 有内链接的日志（课件评论等）2 带图片链接的日志（美好的生活）
    type = models.IntegerField(default=0, verbose_name='日志类型')
    type_id = models.IntegerField(null=True, blank=True)  # 关联的ID，比如课件的ID
    link_name = models.CharField(null=True, blank=True, verbose_name='链接显示名称', max_length=256)
    link_link = models.CharField(verbose_name='链接的http(s)', null=True, blank=True, max_length=256)
    album = models.ForeignKey("bee_django_social_feed.Album", null=True, blank=True, on_delete=models.SET_NULL)
    is_stick = models.BooleanField(default=False, verbose_name='是否置顶')
    stick_expired_at = models.DateTimeField(null=True, blank=True, verbose_name='置顶失效日期')

    is_star = models.BooleanField(default=False, verbose_name='是否精华')
    star_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='由谁加精', related_name='star_operator',
                                null=True, blank=True)
    star_at = models.DateTimeField(null=True, blank=True, verbose_name='加精时间')

    class Meta:
        permissions = [
            ('can_manage_feeds', '能管理日志'),
        ]

    @classmethod
    def create_user_section_note_feed(cls, user, feed_content, type_id, link_name=None, link_link=None):
        return user.feed_set.create(content=truncatewords(feed_content, 140),
                                    type=1, type_id=type_id, link_name=link_name, link_link=link_link)

    def check_link_link(self, user, section_id):
        # 检查user是否学过section_id对应的section 学过就返回True，没学过返回False
        return True

    # manxuetang用户有小图标
    def publisher_icon_list(self):
        return []


class FeedComment(models.Model):
    feed = models.ForeignKey(Feed)
    comment = models.TextField(verbose_name='评论')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(default=timezone.now)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='to_user')


class FeedEmoji(models.Model):
    feed = models.ForeignKey(Feed)
    emoji = models.IntegerField(default=0, verbose_name='感受')  # 0 赞，TODO: 1 笑趴，2 哇，3 心碎，4 怒
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class FeedImage(models.Model):
    feed = models.ForeignKey(Feed, verbose_name='日志')
    image = models.ImageField(verbose_name='图片', upload_to='feeds/%Y/%m/%d')
    created_at = models.DateTimeField(default=timezone.now)
    thumbnail_url = models.CharField(max_length=250, null=True, blank=True)
    medium_url = models.CharField(max_length=250, null=True, blank=True)


class FeedStickSettings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    number = models.IntegerField(default=1, verbose_name='置顶条数')
    duration = models.IntegerField(default=1, verbose_name='置顶天数')

    def __unicode__(self):
        return self.user.first_name or self.user.username


@receiver(post_save, sender=FeedImage)
def resize_feedimage(sender, **kwargs):
    feed_image = kwargs['instance']
    if kwargs['created']:
        resize_image(feed_image.image)
        feed_image.thumbnail_url = resized_image_url(feed_image.image, 'thumbnail')
        feed_image.medium_url = resized_image_url(feed_image.image, 'medium')
        feed_image.save()


class Album(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.TextField(verbose_name='感受')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    # 0 待审核，1 普通，2 优秀，3 未通过
    status = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ('can_manage_album', '能进入Albums管理页'),
        ]

    def create_feed(self):
        image_urls = []
        for i in self.albumphoto_set.all():
            image_urls.append(i.image)
        trunc = Truncator(self.note)

        self.feed_set.create(
            type=2,
            content=trunc.words(1),
            publisher=self.user
        )


class AlbumPhoto(models.Model):
    album = models.ForeignKey(Album, null=True, blank=True)
    image = models.ImageField(verbose_name='图片', upload_to='album_photo/%Y/%m/%d')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(verbose_name='描述')
    thumbnail_url = models.CharField(max_length=250, null=True, blank=True)
    medium_url = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


@receiver(post_save, sender=AlbumPhoto)
def resize_albumphoto(sender, **kwargs):
    album_photo = kwargs['instance']
    if kwargs['created']:
        resize_image(album_photo.image)
        album_photo.thumbnail_url = resized_image_url(album_photo.image, 'thumbnail')
        album_photo.medium_url = resized_image_url(album_photo.image, 'medium')
        album_photo.save()
