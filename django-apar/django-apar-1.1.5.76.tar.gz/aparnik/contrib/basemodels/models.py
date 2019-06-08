# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from polymorphic.models import PolymorphicManager, PolymorphicModel
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

import tagulous

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

    def active(self):
        return self.get_queryset()

    def update_needed(self):
        return self.active().filter(update_needed=True)


# BaseModel class
class BaseModel(PolymorphicModel):
    review_average = models.FloatField(null=True, blank=True, verbose_name=_('Review Average'))

    tags = tagulous.models.TagField(to=Tag, blank=True)
    sort = models.IntegerField(default=0, verbose_name=_('Sort'))
    visit_count = models.IntegerField(default=0, verbose_name=_('Visit counter'))
    update_needed = models.BooleanField(default=False, verbose_name=_('Update needed'))
    is_show_only_for_super_user = models.BooleanField(default=False, verbose_name=_('Show only for super user'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = BaseModelManager()

    def __unicode__(self):
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
        if not user.is_authenticated():
            return False
        from aparnik.contrib.bookmarks.models import Bookmark
        order = Bookmark.objects.filter(user_obj=user, model_obj=self)
        if order.count() > 0:
            return True
        return False

    def is_notify(self, user):
        if not user.is_authenticated():
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
        if not user.is_authenticated():
            return False
        if user.is_superuser or user.is_admin:
            return True
        return False

    def get_user_for_base_review_notification(self, instance, created):
        return User.objects.none()

    def has_permit_edit(self, user):
        return False
