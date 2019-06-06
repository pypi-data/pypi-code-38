# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from robot_detection import is_robot
from pytils import translit

import re
import hashlib

from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

"""Самодельные базовые модели, от которых наследуется модели тестов, категорий"""

"""
USAGE:

class MyModel(ModelWithFieldsHistory):
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if 'name' in self.changed_fields or not self.pk:
            # do something
        super(MyModel, self).save(*args, **kwargs)
"""
class ModelWithFieldsHistory(models.Model):
    def __init__(self, *args, **kwargs):
        super(ModelWithFieldsHistory, self).__init__(*args, **kwargs)
        # Store initial field values into self._original
        self._original = {}
        for field in self._meta.fields:
            try:
                # for foreign keys save in _original field_id instead of field name
                # this is for reducing database hits
                if hasattr(self, field.name + '_id'):
                    fname = field.name + '_id'
                else:
                    fname = field.name
                self._original[fname] = getattr(self, fname)
            except: # DoesNotExist
                self._original[field.name] = None
    
    def _get_changed_fields(self):
        changed = []
        for field in self._meta.fields:
            if hasattr(self, field.name + '_id'):
                fname = field.name + '_id'
            else:
                fname = field.name
            if self._original[fname] != getattr(self, fname):
                changed.append(fname)
        return changed
    
    def _get_original(self):
        return self._original
    
    changed_fields = property(_get_changed_fields)
    original = property(_get_original)
    
    class Meta:
        abstract = True


class ModelWithHits(models.Model):
    hits = models.PositiveIntegerField(_('hits'), default=0, editable=False,
                                       db_index=True)
    
    class Meta:
        abstract = True
    
    def increase_hits(self, ua=None, force=False):
        """Увеличивает счетчик просмотров объекта на единицу"""
        try:
            if force or not is_robot(ua):
                if self.pk:
                    self.hits = F('hits') + 1
                else:
                    self.hits = 1
                return True
        except Exception:
            pass
        return False
    
    def increase_hits_and_save(self, ua=None, force=False):
        done = self.increase_hits(ua, force)
        if done:
            if self.pk:
                return self.save(update_fields=['hits'])
            else:
                return self.save()
        else:
            if self.pk:
                return self
            else:
                # если новый объект сохраняем в любом случае
                return self.save()


class ModelWithSlug(models.Model):
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        unique=True, blank=True, null=True,
        help_text=_('Created from title/name automatically if empty.')
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        self.make_slug()
        return super(ModelWithSlug, self).save(*args, **kwargs)
    
    def make_slug(self):
        # генерируется только один раз
        if not self.slug:
            # search for title field
            title_value = None
            for field in ('title', 'name',):
                if hasattr(self, field) and getattr(self, field):
                    title_value = getattr(self, field)
                    break
            if title_value:
                # заменяем неразрывные пробелы иначе они портят slug
                title_value = title_value.replace("\u00A0", " ")
                slug = translit.slugify(title_value)
                slug = re.sub(r'\-{2,}', '-', slug)
                # nonunique slug generated?
                check = 1
                check_slug = slug
                while(True):
                    if self.__class__.objects.filter(slug=check_slug).exists():
                        check += 1
                        check_slug = slug[0:250]  # обрезаем с запасом
                        check_slug += "-%d" % check
                    else:
                        slug = check_slug
                        break
                self.slug = slug
                return True
        return False


# https://docs.djangoproject.com/en/1.8/topics/migrations/#serializing-values
# If you are using Python 2, we recommend you move your methods for upload_to
# and similar arguments that accept callables (e.g. default) to live in the
# main module body, rather than the class body.
def _uploaded_filename(instance, filename, dt=None):
    """Хешируем имя файла при загрузке, чтобы не хранить русские имена файлов"""
    m = re.search(r'.+?(\.[^.]+)$', filename)
    extension = m.group(1) if m else ''
    # md5 ожидает байты, не юникод!
    filename_hash = hashlib.md5( filename.encode('utf-8') ).hexdigest()
    path = instance._meta.app_label  # например "publication" или "homepage"
    if dt is None:
        dt = timezone.now()
    # в случае совпадения имен, django сам допишет "_random" к имени нового файла
    return "%s/%s/%s/%s/%s%s" % (path, dt.strftime('%Y'), dt.strftime('%m'),
                                  dt.strftime('%d'), filename_hash, extension)


class ModelWithImage(ModelWithFieldsHistory):
    IFNS = ['image',]  # image field names (can be multiple)
    
    image = models.ImageField(
        _('image'), blank=True, null=False, db_index=True,
        upload_to=_uploaded_filename,
        width_field='image_w', height_field='image_h'
    )
    image_w = models.PositiveSmallIntegerField(blank=True, null=True, editable=False)
    image_h = models.PositiveSmallIntegerField(blank=True, null=True, editable=False)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        self._delete_changed_images()
        return super(ModelWithImage, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self._delete_images()
        return super(ModelWithImage, self).delete(*args, **kwargs)
    
    def has_image(self):
        """Для админки"""
        return True if self.image else False
    has_image.boolean = True
    has_image.admin_order_field = 'image'
    has_image.short_description = _('image')
    
    def _delete_changed_images(self):
        """Удаление старого файла(ов) картинки при его изменении"""
        # сохранение поюзанного объекта (в новом не надо удалять старый файл)
        if not self.id:
            return
        for ifn in self.IFNS:
            if ifn in self.changed_fields:  # картинка изменилась
                # старая картинка была вообще?
                if self.original[ifn] \
                and self.original[ifn] != getattr(self, ifn):  
                    storage, path = self.original[ifn].storage,\
                                    self.original[ifn].path
                    storage.delete(path)
    
    def _delete_images(self):
        for ifn in self.IFNS:
            # image for this object exists?
            if getattr(self, ifn):
                storage, path = getattr(self, ifn).storage, getattr(self, ifn).path
                if storage and path:
                    storage.delete(path)
                    setattr(self, ifn, None)
                    setattr(self, ifn+'_h', None)
                    setattr(self, ifn+'_w', None)


class ModelWith2Images(ModelWithImage):
    IFNS = ['image', 'image2']  # redeclare
    
    image2 = models.ImageField(
        _('image 2'), blank=True, null=False, db_index=True,
        upload_to=_uploaded_filename,
        width_field='image2_w', height_field='image2_h'
    )
    image2_w = models.PositiveSmallIntegerField(blank=True, null=True, editable=False)
    image2_h = models.PositiveSmallIntegerField(blank=True, null=True, editable=False)
    
    class Meta:
        abstract = True
    
    def has_image2(self):
        """Для админки"""
        return True if self.image2 else False
    has_image2.boolean = True
    has_image2.admin_order_field = 'image2'
    has_image2.short_description = _('image 2')
    