# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.settings.models import Setting
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager


User = get_user_model()


# Product Sharing
class ProductSharingManager(BaseModelManager):
    def get_queryset(self):
        return super(ProductSharingManager, self).get_queryset()

    def active(self):
        return super(ProductSharingManager, self).active().filter(is_active=True)

    def share_this_user(self, user, product_id=None):
        if not user.is_authenticated:
            return ProductSharing.objects.none()

        # TODO: اضافه کردن این که فقط فعالین را بر گرداند یا خیر !
        queryset = self.active().filter(user_obj=user)
        if product_id:
            queryset = queryset.filter(product_obj__id=product_id)
        return queryset

    def share_with_this_user(self, user, product_id=None):
        queryset = self.active().filter(ProductSharing.query_share_with(user))
        if product_id:
            queryset = queryset.filter(product_obj__id=product_id)
        return queryset


class ProductSharing(BaseModel):

    user_obj = models.ForeignKey(User, related_name='productsharing_user_source', on_delete=models.CASCADE, verbose_name=_('User'))
    user_product_share_with_obj = models.ForeignKey(User, related_name='productsharing_user_product_share_with', on_delete=models.CASCADE, verbose_name=_('Share With'))
    product_obj = models.ForeignKey('products.Product', related_name='productsharing_product', on_delete=models.CASCADE, verbose_name=_('Product'))
    is_active = models.BooleanField(default=False, verbose_name=_('Is Active'))

    objects = ProductSharingManager()

    class Meta:
        verbose_name = _('Product Sharing')
        verbose_name_plural = _('Products Sharing')

    def __str__(self):
        return str(self.user_obj)

    def clean(self):

        if self.user_obj == self.user_product_share_with_obj:
            # both user are the same
            raise ValidationError({
                'user_obj': [_('Both can not have the same values.'), ],
                'user_product_share_with_obj': [_('Both can not have the same values.'), ]
            })
        if self.is_active:
            if not self.product_obj.is_buy(user=self.user_obj):
                raise ValidationError({
                    'user_obj': [_('You must first purchase this item.'), ],
                })

            # بررسی این که این کاربر دسترسی دارد یا خیر
            if self.product_obj.has_permit(user=self.user_product_share_with_obj):
                raise ValidationError({
                    'user_product_share_with_obj': [_('This user already has access to this product.'), ],
                })

            # بررسی دسترسی های داده شده توسط این کاربر برای یک کالای خاص
            max_share_per_product = Setting.objects.get(key='MAX_PRODUCT_SHARING_USER_ALLOWED_PER_PRODUCT').get_value()
            if ProductSharing.objects.share_this_user(product_id=self.product_obj.id, user=self.user_obj).count() > max_share_per_product:
                raise ValidationError({
                    'user_obj': [
                        _('The ceiling for the number of accesses that you could have made for this item is over. Please contact the support team.')
                    ],
                })

            # بررسی کل دسترسی های داده شده توسط این کاربر.
            max_share_for_all_products = Setting.objects.get(key='MAX_PRODUCT_SHARING_USER_ALLOWED_FOR_ALL_PRODUCTS').get_value()
            if ProductSharing.objects.share_this_user(user=self.user_obj).count() > max_share_for_all_products:
                raise ValidationError({
                    'user_obj': [
                        _('The ceiling of the number of accesses you could have completed is over. Please contact the support team.'), ],
                })

        return super(ProductSharing, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_active:
            from aparnik.contrib.notifications.models import Notification
            Notification.objects.send_notification(
                users=[self.user_product_share_with_obj],
                from_user_obj=self.user_obj,
                model_obj=self.product_obj,
                type=Notification.NOTIFICATION_INFO,
                title='اضافه شدن دسترسی',
                description='دسترسی شما به %s توسط %s اضافه شد.' %(self.product_obj.title, self.user_obj.last_name),
            )

        return super(ProductSharing, self).save(*args, **kwargs)

    @staticmethod
    def query_share_with(user, prefix=''):
        field_share_with = 'user_product_share_with_obj'
        if prefix:
            field_share_with = prefix + '__' + field_share_with

        query_filter = Q(**{field_share_with: user})

        return query_filter