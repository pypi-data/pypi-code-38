# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from pytils.translit import translify
from PIL import Image

import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from commonstuff.str_utils import load_class_from_string
from commonstuff.models import PidLock
from commonstuff.settings import CKEDITOR_MODELS, CKEDITOR_MAX_IMAGE_SIZE, \
                                 CKEDITOR_MAX_IMAGE_W, CKEDITOR_MAX_IMAGE_H


class Command(BaseCommand):
    """Консольная команда для чистки файлов, загружаемых авторами для контента."""
    
    help = 'Deletes unused ckeditor uploads and optimizes other ckeditor uploaded images.'
    
    logger = None
    pid_lock = None
    
    do_all_files = False
    ckeditor_upload_path = None
    model_classes = []
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        
        # защита от нескольких работающих копий скрипта
        self.pid_lock = PidLock(process=__file__)
        self.pid_lock.save_or_die()
        
        # все что после save_or_die может не выполниться,
        # если другой процесс уже выполняет эту команду
        
        log_file = os.path.join(settings.BASE_DIR, 'log', 'ckeditoruploads.log')
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler(log_file))
    
    def __del__(self):
        if self.pid_lock and self.pid_lock.pk:
            self.pid_lock.delete()
    
    def add_arguments(self, parser):
        parser.add_argument('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Work with all ckeditor images instead of yesterday images only.')
    
    def check_conf(self):
        if not CKEDITOR_MODELS:
            e = 'В settings.py не настроено DJANGO_COMMONSTUFF_CKEDITOR_MODELS. '
            e += 'См. docs/SETTINGS.rst за подробностями.'
            raise CommandError(translify(e))
        if CKEDITOR_MAX_IMAGE_SIZE < 50:
            raise CommandError(translify(
                "Меньше 50 кб максимальный размер файла? Будь реалистом. " + \
                "Эта команда для обработки реально больших файлов, " + \
                "которые забивают сеть и диски. См. docs/SETTINGS.rst за подробностями."
            ))
        if CKEDITOR_MAX_IMAGE_W < 300 or CKEDITOR_MAX_IMAGE_H < 300:
            raise CommandError(translify(
                "Слишком маленькая максимальная ширина x высота картинок " + \
                "для ресайза. См. docs/SETTINGS.rst за подробностями."
            ))
    
    def init_vars(self):
        # отдельный метод, чтобы запускался после проверки настроек
        self.ckeditor_upload_path = os.path.join(settings.MEDIA_ROOT,
                                                 settings.CKEDITOR_UPLOAD_PATH)
        
        for class_string, field_name in CKEDITOR_MODELS:
            self.model_classes.append(
                [ load_class_from_string(class_string), field_name ]
            )
    
    def handle(self, *args, **options):
        self.check_conf()
        self.init_vars()
        self.do_all_files = options['all']
        
        self.delete_unused_files()
        self.resize_big_images()
        self.logger.info("")
    
    def _get_file_list(self):
        path_substring = None if self.do_all_files \
                            else (now()-timedelta(days=1)).strftime("/%Y/%m/%d/")
        uploads = []
        for path, subdirs, files in os.walk(self.ckeditor_upload_path, 
                                            followlinks=True):
            for filename in files:
                f = os.path.join(path, filename)  # absolute file path
                if self.do_all_files or path_substring in f:
                    uploads.append(f)
        return uploads
    
    def delete_unused_files(self):
        """
        Удаляем файлы, которые были загружены, а потом не использованы в теле
        контента (статьи, рассылки).
        """
        def _used_in_content(web_path):
            for cls, field in self.model_classes:
                kwargs = { '%s__contains' % field : web_path }
                if cls.objects.filter(**kwargs).exists():
                    return True
            return False
        
        uploads = self._get_file_list()
        self.logger.info("%d files to check for usage in content." % len(uploads))
        
        # ищем файлы на удаление
        to_delete = []
        for f in uploads:
            rel_f = os.path.relpath(f, self.ckeditor_upload_path)
            web_path = "/".join([settings.MEDIA_URL, settings.CKEDITOR_UPLOAD_PATH, rel_f])
            web_path = web_path.replace('//', '/')  # как этот файл будет адресован из веба
            if not _used_in_content(web_path):
                to_delete.append(f)
        
        # если их найдено ооочень много, то это скорее проблемы с конфигурацией модели
        if len(to_delete) > 30 and len(to_delete) > len(uploads)*0.25:
            e = translify(
                "Команда собиралась удалить более 25% загруженных файлов " + \
                "(%d из %d). " % (len(to_delete), len(uploads)) + \
                "Это слишком много и подозрительно. " + \
                "Пожалуйста, проверьте настройки команды. Файлы не удалены."
            )
            self.logger.error(e)
            raise CommandError(e)
        
        deleted_size = 0
        for f in to_delete:
            deleted_size += os.path.getsize(f)
            self.logger.debug("%s deleted." % f)
            os.unlink(f)
        self.logger.info(
            "%d unused uploads deleted, total size of %d mb." % \
            (len(to_delete), round(deleted_size/(1024*1024)))
        )
    
    def resize_big_images(self):
        uploads = self._get_file_list()
        self.logger.info("%d files to check for resize." % len(uploads))
        
        saved_size = 0
        counter = 0
        for f in uploads:
            f_size = os.path.getsize(f)
            if f_size > CKEDITOR_MAX_IMAGE_SIZE*1024:
                try:
                    with Image.open(f) as img:
                        w, h = img.size
                        if w > CKEDITOR_MAX_IMAGE_W or h > CKEDITOR_MAX_IMAGE_H:
                            self.logger.debug(
                                "Image %s is %.2f mb and %d*%d px." % 
                                (f, f_size*1.0/(1024*1024), w, h)
                            )
                            # метод thumbnail сам разрулит aspect ratio
                            # размеры в данном случае - это максимальные значения
                            img.thumbnail((CKEDITOR_MAX_IMAGE_W, CKEDITOR_MAX_IMAGE_H), Image.ANTIALIAS)
                            img.save(f, optimize=True, quality=85)
                            
                            counter += 1
                            saved_size += (f_size - os.path.getsize(f))
                except IOError as e:
                    self.logger.error(
                        "%s seems to be not an image of supported type: %s." %
                        (f, e)
                    )
        self.logger.info(
            "%d files optimized, saved %d mb." %
            (counter, round(saved_size/(1024*1024)))
        )
        