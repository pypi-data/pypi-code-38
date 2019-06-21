from django.contrib import admin
from autopost.models import AutoTask, Article, Category, Author, RemoteImages
from autopost.utils.html import HtmlStorage
from django.utils.html import format_html
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from system.utils import tools
import os
from system.utils.Cipher import QTCipher
from django.conf import settings
from crontab import CronTab, CronItem
from .forms import ArticleForm
from taggit_helpers.admin import TaggitCounter, TaggitStackedInline, TaggitTabularInline
from uuslug import slugify, uuslug


def mgr_crontab(sender, instance, created, **kwargs):
    if hasattr(settings, 'CRONTAB_TO_FILE') and not settings.CRONTAB_TO_FILE:
        return False
    crontab_name = QTCipher.md5('mgr_crontab' + str(instance.id))
    cron_path = os.path.join(settings.BASE_DIR, 'qt_cron')
    venv_python = os.path.join(settings.BASE_DIR, 'venv/bin/python')
    if not os.path.exists(cron_path):
        os.mkdir(cron_path)
    cron_file = os.path.join(cron_path, crontab_name)
    with open(cron_file, 'w+') as f:
        cron_content = """#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export PROJECT_ENV={env}
{python} {base_path}/manage.py autopost {auto_id}
echo "----------------------------------------------------------------------------"
endDate=$(date "+%Y-%m-%d %H:%M:%S")
echo "**[$endDate] Successful**"
echo "----------------------------------------------------------------------------"
"""
        f.write(cron_content.format(env=settings.ENV_CONFIG, python=venv_python, base_path=settings.BASE_DIR,
                                    auto_id=instance.id))
    os.system('chmod -R 777 ' + cron_file)
    # 读取当前用户的crontab
    user_crontab = CronTab(user=settings.CRONTAB_USER)
    jobs = user_crontab.find_comment(crontab_name)
    job = None
    for item in jobs:
        if item.comment == crontab_name:
            job = item
            break

    if created or not job:
        job = user_crontab.new(cron_file + ' >> ' + cron_file + '.log')
        job.set_comment(crontab_name)
    job.enable(instance.enable)
    # 设置任务执行时间
    job.setall(instance.crontab)
    user_crontab.write()


post_save.connect(mgr_crontab, sender=AutoTask)


@receiver(post_delete, sender=AutoTask)
def del_crontab(sender, instance, *args, **kwargs):
    if hasattr(settings, 'CRONTAB_TO_FILE') and not settings.CRONTAB_TO_FILE:
        return False
    crontab_name = QTCipher.md5('mgr_crontab' + str(instance.id))
    cron_path = os.path.join(settings.BASE_DIR, 'qt_cron')
    if not os.path.exists(cron_path):
        os.mkdir(cron_path)
    user_crontab = CronTab(user=settings.CRONTAB_USER)
    jobs = user_crontab.find_comment(crontab_name)
    job = None
    for item in jobs:
        if item.comment == crontab_name:
            job = item
            break
    user_crontab.remove(job)
    user_crontab.write()


@admin.register(AutoTask)
class AutoTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'crontab', 'url', 'site', 'category', 'enable', 'operate_crawl')
    list_display_links = ('id', 'title')
    list_filter = ('site', 'category')
    list_editable = ('crontab', 'enable')
    fieldsets = (
        ('基础设置', {'fields': ['title', 'url', 'crontab', 'enable']}),
        ('文章列表', {'fields': ['list_selector', 'page_selector', 'preview_title_btn']}),
        ('文章内容',
         {'fields': ['title_selector', 'content_selector', 'content_except', 'lazy_photo',
                     'title_replace', 'content_replace', 'preview_detail_btn']}),
        ('发布设置', {'fields': ['site', 'category', 'source', 'author']}),
    )
    readonly_fields = ('preview_title_btn', 'preview_detail_btn')

    class Media:
        js = ('qt_admin/js/autopost.js',)
        css = {'all': ('qt_admin/css/bootstrap.css',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'get_site', 'publish_url', 'recommend_type', 'status', 'created')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    list_filter = ('site', 'category')
    list_editable = ('recommend_type',)
    fieldsets = (
        ('基础设置', {'fields': ['site', 'category', 'author', 'type', 'link_address']}),
        ('文章信息', {'fields': ['title', 'upload_docx', 'content']}),
        ('高级设置',
         {'fields': ['slug', 'keywords', 'summery', 'recommend_type', 'thumbnail',
                     'visits', 'clear_link', 'save_img', 'status', 'allow_comments', 'tags']}),
    )
    readonly_fields = ('upload_docx',)
    inlines = [TaggitTabularInline]
    form = ArticleForm

    def get_site(self, obj):
        return obj.category.site.name

    def publish_url(self, obj):
        purl = 'http://%s/news/%d.html' % (obj.category.site.domain, obj.id)
        return format_html('<a href="{url}" target="_blank">{url}</a>'.format(url=purl))

    get_site.short_description = '所属站点'
    publish_url.allow_tags = True
    publish_url.short_description = '发布URL'

    class Media:
        js = ('qt_admin/layui/layui.js', 'qt_admin/js/article.js')
        css = {'all': ('qt_admin/layui/css/layui.css',)}

    def save_model(self, request, obj, form, change):
        html_content, first_img, key_list, summery = HtmlStorage.save_content(content=obj.content,
                                                                              save_img=obj.save_img,
                                                                              remove_a=obj.clear_link,
                                                                              send_qiniu=True)
        obj.content = html_content
        if obj.thumbnail == '' and first_img:
            # 去掉前面/
            if first_img.startswith('/'):
                obj.thumbnail = first_img[1:]
            else:
                obj.thumbnail = first_img
        obj.keywords = ','.join(key_list)

        if not obj.slug:
            obj.slug = uuslug(obj.title, obj, max_length=25, word_boundary=True)

        if not obj.summery and summery:
            obj.summery = summery
        super(ArticleAdmin, self).save_model(request, obj, form, change)
        # 去除自动创建TAG, 无实际使用意义
        # if len(post_data['tags']) == 0:
        #     for tmp_key in key_list[:3]:
        #         obj.tags.add(tmp_key)
        #     obj.save()


def article_save(sender, instance, created, **kwargs):
    """
    推送文章到百度
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if hasattr(settings, 'CRONTAB_TO_FILE') and not settings.CRONTAB_TO_FILE:
        return False
    if created:
        scheme = 'https' if instance.site.siteproperty.scheme else 'http'
        url = '%s://%s/news/%d.html' % (scheme, instance.site.domain, instance.id)
        tools.push_baidu(url, instance.title, instance.site)


post_save.connect(article_save, sender=Article)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created', 'updated']
    list_display_links = ('id', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'slug', 'site', 'status', 'created')
    list_display_links = ('id', 'name')
    list_filter = ('site',)
    list_editable = ('slug', 'status')


@admin.register(RemoteImages)
class RemoteImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'origin_src', 'local_src', 'remote_src', 'created')
    list_display_links = ('id', 'file_name')
    list_filter = ('file_name', 'remote_src', 'origin_src')
