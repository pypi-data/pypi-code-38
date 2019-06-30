# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q, Count, F
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.core.validators import ValidationError
# from polymorphic.models import PolymorphicModel, PolymorphicManager
from aparnik.contrib.basemodels.models import BaseModel
from aparnik.utils.utils import field_with_prefix

User = get_user_model()


# Bookmark MANAGER
class BookmarkManager(models.Manager):

    def get_queryset(self):
        return super(BookmarkManager, self).get_queryset()

    def active(self, user=None):
        return self.get_queryset()

    def models(self, model):
        return self.get_queryset().filter(model_obj=model)

    def get_this_user(self, user):
        if not user.is_authenticated:
            return Bookmark.objects.none()
        return self.get_queryset().filter(user_obj=user)


# Bookmark MODEL
class Bookmark(models.Model):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    model_obj = models.ForeignKey(BaseModel, related_name='bookmark_obj', on_delete=models.CASCADE, verbose_name=_('Model'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = BookmarkManager()

    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')

    def __str__(self):
        return "%s" % self.id

    def clean(self):
        bookmark = Bookmark.objects.models(model=self.model_obj).filter(user_obj=self.user_obj)

        if bookmark.count() == 1 and self.id != bookmark.first().id:
            raise ValidationError(
                {'user_obj': [_('You can\'t Bookmark again.')], 'model_obj': [_('You can\'t Bookmark again')]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Bookmark, self).save(*args, **kwargs)

    def get_api_uri(self):
        return reverse('aparnik-api:bookmarks:detail', args=[self.id])

    # def get_api_like_uri(self):
    #     return reverse('api:qa:like:list', args=[self.id])

    @staticmethod
    def sort_bookmark(return_key='bookmark_count', prefix=''):
        sort = {
            return_key: {
                'label': 'بوکمارک',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Count(
                            field_with_prefix('id', prefix),
                        )
                },

                'key_sort': 'sort_count',
            }
        }
        return sort
