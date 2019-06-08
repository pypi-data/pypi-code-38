# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.utils.text import Truncator

from aparnik.settings import Setting
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.packages.educations.courses.models import Course
from aparnik.contrib.notifications.models import Notification

User = get_user_model()


# Total Time Manager
class ReviewSummaryManager(models.Manager):

    def get_queryset(self):
        return super(ReviewSummaryManager, self).get_queryset()


class ReviewSummary(models.Model):
    rate = models.CharField(max_length=1, verbose_name=_('Rate'))
    count = models.BigIntegerField(default=0, verbose_name=_('Count'))
    percentage = models.FloatField(verbose_name=_('Percentage'))
    model = models.ForeignKey(BaseModel, related_name='review_summaries', verbose_name=_('Models'))

    objects = ReviewSummaryManager()

    class Meta:
        verbose_name = _('Reivew Summary')
        verbose_name_plural = _('Review Summary')

    def __unicode__(self):
        return '%s' % self.id


# Review Manager
class BaseReviewManager(BaseModelManager):
    def get_queryset(self):
        return super(BaseReviewManager, self).get_queryset()

    def get_this_user(self, user):
        if not user.is_authenticated():
            return BaseReview.objects.none()
        return self.get_queryset().filter(user_obj=user)

    def active(self):
        return super(BaseReviewManager, self).filter(is_published=True)

    def model_base_reviews(self, model_obj, user_obj=None, with_children=False):
        if not isinstance(model_obj, BaseModel):
            model_obj = BaseModel.objects.get(pk=model_obj)

        objs = self.active().filter(model_obj=model_obj)
        if not with_children:
            objs = objs.filter(parent_obj__isnull=True)
        if user_obj:
            query = objs | self.get_queryset().filter(model_obj=model_obj, parent_obj__isnull=True)
            if model_obj.has_permit_full_access(user_obj):
                return query
            elif isinstance(model_obj, Course):
                if model_obj.teachers.all().filter(user_obj=user_obj).exists():
                    # Teacher mode
                    return query
            # get user base review add
            return objs | self.get_queryset().filter(model_obj=model_obj, parent_obj__isnull=True,
                                                     user_obj=user_obj, is_published=False)
        return objs


# Review Model
class BaseReview(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_published = models.BooleanField(default=False, verbose_name=_('Published'))
    # ابجکتی که نظر براش ثبت شده به عنوان مثال کالای اول
    model_obj = models.ForeignKey(BaseModel, related_name='review_obj', verbose_name=_('Model'))
    user_obj = models.ForeignKey(User, verbose_name=_('User'))
    parent_obj = models.ForeignKey('self', related_name='child', blank=True, null=True, verbose_name=_('Parent'))

    objects = BaseReviewManager()

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(BaseReview, self).__init__(*args, **kwargs)

    def clean(self):

        if self.id:
            obj = BaseReview.objects.get(id=self.id)
            if self.is_published != obj.is_published:
                pass
                # TODO: check permission

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.id:
            self.update_needed = True
        return super(BaseReview, self).save(*args, **kwargs)

    def get_api_like_uri(self):
        return reverse("aparnik-api:reviews:like:list", kwargs={"review_id": self.id})

    def get_api_dislike_uri(self):
        return reverse("aparnik-api:reviews:dislike:list", kwargs={"review_id": self.id})

    def get_api_action_like(self):
        return reverse("aparnik-api:reviews:like:set", kwargs={"review_id": self.id})

    def get_api_action_dislike(self):
        return reverse("aparnik-api:reviews:dislike:set", kwargs={"review_id": self.id})

    def get_api_action_base_review_status_set(self):
        return reverse("aparnik-api:reviews:status-set", kwargs={"review_id": self.id})

    class Meta:
        verbose_name = _('Base Review')
        verbose_name_plural = _('Base Reviews')

    def has_permit_replay(self, user):
        if not user.is_authenticated():
            return False
        if self.has_permit_full_access(user):
            return True
        # اگر پدر نداشت مجوز پاسخ را دارد. باید سطح دسترسی فقط کنترل شود.
        return self.parent_obj is None

    def has_permit_change_status(self, user):
        if not user.is_authenticated():
            return False
        if self.has_permit_full_access(user):
            return True
        return self.model_obj.get_real_instance().has_permit_edit(user=user)

    def has_permit_edit(self, user):
        if not user.is_authenticated():
            return False
        if self.has_permit_full_access(user):
            return True
        return self.model_obj.get_real_instance().has_permit_edit(user=user)

    def is_like(self, user):
        return self.like_set.filter(user_obj=user, is_like=True).exists()

    def is_dislike(self, user):
        return self.like_set.filter(user_obj=user, is_like=False).exists()


# Review Manager
class ReviewManager(BaseReviewManager):

    def get_queryset(self):
        return super(ReviewManager, self).get_queryset()

    def get_this_user(self, user):
        return super(ReviewManager, self).get_this_user(user=user)

    def model_reviews(self, model_obj, user_obj=None, with_children=False):
        return super(ReviewManager, self).model_base_reviews(model_obj, user_obj, with_children)

    def model_review_count(self, model_obj, user_obj=None):
        return self.model_reviews(model_obj, user_obj, with_children=True).count()

    def model_review_avg(self, model_obj):
        return self.model_reviews(model_obj).aggregate(review_average=Avg('rate'))['review_average']


# Review Model
class Review(BaseReview):
    rate = models.FloatField(verbose_name=_('Rate'))

    objects = ReviewManager()

    def __unicode__(self):
        return '{} {}'.format(self.title, self.rate)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')


# LIKE MANAGER
class LikeManager(models.Manager):

    def get_queryset(self):
        return super(LikeManager, self).get_queryset()

    def get_this_user(self, user):
        if not user.is_authenticated():
            return Like.objects.none()
        return self.get_queryset().filter(user=user)

    def review(self, review_obj):
        return self.get_queryset().filter(review_obj=review_obj)

    def like(self, review_obj):
        return self.review(review_obj=review_obj).filter(is_like=True)

    def dislike(self, review_obj):
        return self.review(review_obj=review_obj).filter(is_like=False)

    def likes_count(self, review_obj):
        return self.like(review_obj=review_obj).count()

    def dislikes_count(self, review_obj):
        return self.dislike(review_obj=review_obj).count()


# LIKE MODEL
class Like(models.Model):
    review_obj = models.ForeignKey(BaseReview, verbose_name=_('Review'))
    is_like = models.BooleanField(default=False, verbose_name=_('Is Like'))
    user_obj = models.ForeignKey(User, verbose_name=_('User'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = LikeManager()

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')

    def __unicode__(self):
        return "%s" % (self.id)

    def clean(self):

        queryset = Like.objects.review(review_obj=self.review_obj).filter(user_obj=self.user_obj)

        if queryset.count() == 1 and self.id != queryset.first().id:

            raise ValidationError({'user_obj': [_('You can\'t like again.')], 'review_obj': [_('You can\'t like again')]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Like, self).save(*args, **kwargs)

    def get_api_uri(self):
        return reverse('aparnik-api:reviews:like:detail', args=[self.review_obj.id, self.id])


# Base Segment Model
class BaseReviewSegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(BaseReviewSegment, self).__unicode__()

    class Meta:
        verbose_name = _('Review Segment')
        verbose_name_plural = _('Reviews Segments')


def post_save_base_review_receiver(sender, instance, created, *args, **kwargs):

    approve = Setting.objects.get(key='APPROVE_REVIEW').get_value()
    model_obj = instance.model_obj.get_real_instance()
    users = User.objects.none()
    verbose_name = instance._meta.verbose_name
    title = '%s %s جدیدی در %s درج کرد' % (instance.user_obj.get_full_name(), verbose_name, model_obj.get_title())
    description = Truncator(instance.title + ' ' + instance.description).words(30)

    if created:
        if approve:
            instance.is_published = True
            instance.save()
            return
        # admin
        if not instance.user_obj.is_admin:
            users = User.objects.admins()

        users |= model_obj.get_user_for_base_review_notification(instance, created)

    else:
        # notify user change state
        if not approve:
            Notification.objects.send_notification(
                users=[instance.user_obj],
                type=Notification.NOTIFICATION_INFO,
                title='وضعیت %s شما تغییر کرده است.' %verbose_name,
                description=description,
                model_obj=instance,
            )

        # send notification for users
        if instance.parent_obj and instance.is_published:
            # replay before
            users = users | User.objects.filter(
                pk__in=BaseReview.objects.active().filter(parent_obj=instance.parent_obj).values_list('user_obj', flat=True)
            )
            # questions
            users |= User.objects.filter(pk=instance.parent_obj.user_obj.pk)

            users |= model_obj.get_user_for_base_review_notification(instance, created)

    users = users.exclude(pk=instance.user_obj.pk)
    users = users.distinct()

    Notification.objects.send_notification(
        users=users,
        type=Notification.NOTIFICATION_INFO,
        title=title,
        description=description,
        model_obj=instance,
        from_user_obj=instance.user_obj,
    )


# post_save.connect(post_save_base_review_receiver, sender=BaseReview)
# connect all subclasses of base content item too
for subclass in BaseReview.__subclasses__():
    post_save.connect(post_save_base_review_receiver, subclass)
