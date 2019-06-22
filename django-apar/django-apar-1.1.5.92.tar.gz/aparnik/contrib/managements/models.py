# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.db import transaction
from django.apps import apps

from aparnik.settings import Setting

User = get_user_model()


# Create your models here.
class ManagementActionsManager(models.Manager):
    def get_queryset(self):
        return super(ManagementActionsManager, self).get_queryset()


class ManagementActions(models.Model):
    title = models.CharField(max_length=50, verbose_name=_('Function title'))
    description = models.CharField(max_length=100, verbose_name=_('Description'))

    objects = ManagementActionsManager()

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Admin action')
        verbose_name_plural = _('Admin actions')


class ManagementPermissionManager(models.Manager):
    def get_queryset(self):
        return super(ManagementPermissionManager, self).get_queryset()


class ManagementPermission(models.Model):
    # MANAGEMENT_PERMISSIONS = ['view','edit','readonly','delete']
    title = models.CharField(max_length=50, verbose_name=_('Title'))
    description = models.CharField(max_length=100, verbose_name=_('Description'))

    objects = ManagementPermissionManager()

    def __str__(self):
        return str(self.title)


class FieldListManager(models.Manager):
    def get_queryset(self):
        return super(FieldListManager, self).get_queryset()

    def update_fields(self, group_id):
        try:
            management_update_enable_status = Setting.objects.get(key='MANAGEMENT_DEFAULT_ENABLE_STATUS').get_value()
        except:
            management_update_enable_status = False

        managementActions = apps.get_model('managements', 'ManagementActions').objects.all()
        managementPermission = apps.get_model('managements', 'ManagementPermission').objects.all()
        # pk = 1;
        # First remove fields which not assigned to a group
        # FieldList.objects.filter(group__isnull=True).delete()

        for app in apps.get_models():
            for name in app._meta.get_fields(include_parents=True):
                with transaction.atomic():
                    field_type = name.get_internal_type()
                    if field_type in ['ForeignKey', 'ManyToManyField', 'OneToOneField', ]:
                        default_value = None

                    if field_type in ['FloatField', 'DecimalField', 'PositiveIntegerField', 'IntegerField',
                                      'BooleanField',
                                      'CharField',
                                      'TextField']:
                        default_value = None

                    if field_type in 'DateTimeField':
                        default_value = None

                    if field_type in 'AutoField':
                        default_value = None

                    if name.name in ['publish_day', 'publish_week', 'publish_month']:
                        default_value = None

                    field_exist = FieldList.objects.filter(model=app._meta.object_name, group_id=group_id,
                                                           name=name.name).count()

                    ## Currently django does not support bulk create with many-to-many felids.
                    if (field_exist == 0):
                        field = FieldList.objects.create(model=app._meta.object_name, name=name.name,
                                                         is_enable=management_update_enable_status, group_id=group_id,
                                                         is_sharable=False, default=default_value)

                        for permission in managementPermission:
                            field.permission.add(permission)
                        for action in managementActions:
                            field.actions.add(action)


class FieldList(models.Model):
    FIELD_LIST = []
    MODELS_LIST = []
    model = models.CharField(max_length=100, verbose_name=_('model'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('group'))
    actions = models.ManyToManyField(ManagementActions, verbose_name=_('Actions'))
    permission = models.ManyToManyField(ManagementPermission, verbose_name=_('Management Permission'))
    is_enable = models.BooleanField(default=True, verbose_name=_('Is enable'))
    is_sharable = models.BooleanField(verbose_name=_('Is sharable'))
    default = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Default'))

    objects = FieldListManager()

    def __init__(self, *args, **kwargs):
        super(FieldList, self).__init__(*args, **kwargs)

    def __str__(self):
        return str(self.model + '.' + self.name)

    class Meta:
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')


class ManagementManager(models.Manager):
    def get_queryset(self):
        return super(ManagementManager, self).get_queryset().all()

    def active(self):
        return self.get_queryset().filter(is_active=True, start_date__lte=now()).filter(
            (Q(end_date__gte=now()) | Q(end_date__isnull=True))).all()

    def get_permissions(self, group):
        return self.active().filter(group__in=[group], fields__is_enable=True).all()

    def get_actions(self, group):
        return self.active().filter(group=group).values_list('actions').all()

    def has_permit(self, group, allowed_permissions):
        if len(self.get_permissions(group)) < len(allowed_permissions):
            return False, 'Exceed parent permissions'
        for permit in allowed_permissions:
            if permit not in self.get_permissions(group):
                return False, permit
        return True

    def update_apps(self, group_id):
        for app in apps.get_app_configs():
            appModels = [model._meta.object_name for model in list(app.get_models(app.label))]
            fieldList = apps.get_model('managements', 'FieldList').objects.filter(model__in=appModels)
            if len(appModels) > 0 and len(fieldList) > 0:

                with transaction.atomic():
                    app_exist = Management.objects.filter(group_id=group_id, application=app.label).count()

                    if (app_exist == 0):
                        management = Management(group_id=group_id, application=app.label, start_date=now(),
                                                is_active=True)
                        management.save({'is_superuser': True})
                        for field in fieldList:
                                management.fields.add(field)
                    else:
                        management = Management.objects.filter(group_id=group_id, application=app.label).first()
                        for field in fieldList:
                            if field not in list(management.fields.all()):
                                management.fields.add(field)
                        management.save({'is_superuser': True})


class Management(models.Model):
    MODELS_NAME_LIST = []
    APPS_LABEL = []
    CONSTRAINTS_SET = []
    ROLES_SET = []

    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('group'))
    application = models.CharField(max_length=100, verbose_name=_('Application'))
    fields = models.ManyToManyField(FieldList, verbose_name=_('fields'))

    parent_obj = models.ForeignKey('self', null=True, on_delete=models.CASCADE, verbose_name=_('Parent'))

    constraint = models.CharField(max_length=200, choices=CONSTRAINTS_SET, verbose_name=_('constraints'))

    start_date = models.DateTimeField(default=now, verbose_name=_('Start date'))

    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('End date'))

    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = ManagementManager()

    def __str__(self):
        return str(self.group)

    def save(self, *args, **kwargs):
        if ('is_superuser' not in kwargs) and len(
                args) == 0:  # To handel requests from management migration or admin update
            (has_permit, unauthorized_permission) = Management.objects.has_permit(self.group, self.allowed_permissions)
        else:
            has_permit = True
            unauthorized_permission = []
        if has_permit or self.is_superuser or kwargs['is_superuser']:
            kwargs.pop('is_superuser', None)  # No need to pass this variable to upper class
            args = ()
            super(Management, self).save(*args, **kwargs)
        else:
            raise ValidationError(
                message=_('Not authorized to designate permission: %s' % str(unauthorized_permission)))

    class Meta:
        verbose_name = _('Admin Permission')
        verbose_name_plural = _('Admin Permissions')


class ManagementRolesManager(models.Manager):
    def get_queryset(self):
        return super(ManagementRolesManager, self).get_queryset()


class ManagementRoles(models.Model):
    title = models.CharField(max_length=30, verbose_name=_('Role name'))
    management_obj = models.ForeignKey(Management, on_delete=models.CASCADE, verbose_name=_('Management group'))

    objects = ManagementRolesManager()

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
