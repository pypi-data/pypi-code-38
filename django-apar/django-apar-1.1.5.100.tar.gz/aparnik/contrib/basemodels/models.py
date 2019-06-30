# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Count, Q, F, Sum
from django.db.models.functions import Coalesce
from polymorphic.models import PolymorphicManager, PolymorphicModel
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.contrib.auth import get_user_model

import tagulous

from aparnik.utils.utils import human_format, field_with_prefix

User = get_user_model()


# BaseModel MANAGER
class Tag(tagulous.models.TagModel):
    class TagMeta:
        # Tag options
        # initial = "eating, coding, gaming"
        # force_lowercase = True
        pass

    def get_api_uri(self):
        return reverse('aparnik-api:models:tags-details', args=[self.id])


class BaseModelManager(PolymorphicManager):

    def get_queryset(self):
        return super(BaseModelManager, self).get_queryset()

    def active(self, user=None):
        return self.get_queryset()

    def update_needed(self):
        return self.active().filter(update_needed=True)


# BaseModel class
class BaseModel(PolymorphicModel):
    review_average = models.FloatField(default=0.0, verbose_name=_('Review Average'))

    tags = tagulous.models.TagField(to=Tag, blank=True)
    sort = models.IntegerField(default=0, verbose_name=_('Sort'))
    visit_count = models.IntegerField(default=0, verbose_name=_('Visit counter'))
    update_needed = models.BooleanField(default=False, verbose_name=_('Update needed'))
    is_show_only_for_super_user = models.BooleanField(default=False, verbose_name=_('Show only for super user'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = BaseModelManager()
    
    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Base Model')
        verbose_name_plural = _('Bases Models')

    def get_api_uri(self):
        return reverse('aparnik-api:models:details', args=[self.id])

    def get_api_review_uri(self):
        return reverse('aparnik-api:reviews:models-list', args=[self.id])

    def get_api_qa_uri(self):
        return reverse('aparnik-api:qa:models-list', args=[self.id])

    def get_api_qa_add_uri(self):
        return reverse('aparnik-api:qa:create', args=[])

    def is_bookmark(self, user):
        if not user.is_authenticated:
            return False
        from aparnik.contrib.bookmarks.models import Bookmark
        order = Bookmark.objects.filter(user_obj=user, model_obj=self)
        if order.count() > 0:
            return True
        return False

    def is_notify(self, user):
        if not user.is_authenticated:
            return False
        from aparnik.contrib.notifiesme.models import NotifyMe
        notifies = NotifyMe.objects.active().filter(user_obj=user, model_obj=self)
        if notifies.count() > 0:
            return True
        return False

    def get_title(self):
        return ''

    def get_api_share_uri(self):
        return reverse('aparnik-api:models:share-content', args=[self.id])

    def get_api_notify_me_set_uri(self):
        return reverse('aparnik-api:notifiesme:set', args=[self.id])

    def get_api_bookmark_set_uri(self):
        return reverse('aparnik-api:bookmarks:set', args=[self.id])

    def get_api_review_add_uri(self):
        return reverse('aparnik-api:reviews:create', args=[])

    def has_permit_full_access(self, user):
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.is_admin:
            return True
        return False

    def get_user_for_base_review_notification(self, instance, created):
        return User.objects.none()

    def has_permit_edit(self, user):
        return False

    @property
    def resourcetype(self):
        return self._meta.object_name

    @property
    def review_count(self):
        return self.reviews_set.active().count()

    @property
    def review_count_string(self):
        return human_format(self.review_count)

    @property
    def qa_count(self):
        return self.question_answers_set.active().count()

    @property
    def qa_count_string(self):
        return human_format(self.qa_count)

    @property
    def bookmark_count(self):
        return self.bookmark_obj.active().count()

    @property
    def bookmark_count_string(self):
        return human_format(self.bookmark_count)

    @property
    def visit_count_string(self):
        return human_format(self.visit_count)

    @staticmethod
    def sort_visit(return_key='visit', prefix=''):
        sort = {
            return_key: {
                'label': 'نمایش',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Coalesce(Sum(field_with_prefix('visit_count', prefix)), 0)
                },
                'key_sort': 'sort_count',
            }
        }
        return sort
