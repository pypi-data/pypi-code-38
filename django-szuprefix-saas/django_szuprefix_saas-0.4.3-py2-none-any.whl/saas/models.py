# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.functional import cached_property
from treebeard.al_tree import AL_Node

from django_szuprefix.utils import modelutils
from . import choices
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Party(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "团体"

    name = models.CharField("名称", max_length=128)
    slug = models.CharField("编号", max_length=16, blank=True)
    status = models.PositiveSmallIntegerField("状态", choices=choices.CHOICES_PARTY_STATUS,
                                              default=choices.PARTY_STATUS_TEST)
    is_active = models.BooleanField("有效", default=True)
    worker_count = models.PositiveIntegerField("用户规模", blank=True, default=0)
    type = models.PositiveSmallIntegerField("类别", blank=True, choices=choices.CHOICES_PARTY_TYPE,
                                            default=choices.PARTY_TYPE_COMPANY)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.name.replace(" ", "")
        if not self.slug:
            self.slug = "og%s" % get_random_string(14, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
        return super(Party, self).save(**kwargs)

    @cached_property
    def root_department(self):
        if self.departments.count() == 0:
            root = self.departments.create(name=self.name)
        else:
            root = self.departments.get(parent__isnull=True)
            if root.name != self.name:
                root.name = self.name
                root.save()
        return root

    @cached_property
    def manager_worker(self):
        name = group_name = '%s管理员' % self.get_type_display()
        worker = self.workers.filter(name=name).first()
        if not worker:
            worker = self.workers.create(name=name)
            worker.departments = [self.root_department]
            from django.contrib.auth.models import Group
            g = Group.objects.filter(name=group_name).first()
            if g:
                worker.user.groups.add(g)
        return worker


class Department(AL_Node):
    class Meta:
        verbose_name_plural = verbose_name = "部门"
        unique_together = ("party", "parent", "name")

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name,
                              related_name="departments")
    parent = models.ForeignKey("Department", verbose_name="上级", null=True, related_name="sub_departments")
    name = models.CharField("名字", max_length=64)
    order_num = models.PositiveSmallIntegerField("序号", default=0, blank=True)
    is_active = models.BooleanField("是否在用", default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    node_order_by = ("order_num",)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if not hasattr(self, 'party') and hasattr(self, 'parent'):
            self.party = self.parent.party
        return super(Department, self).save(**kwargs)

    def get_sub_department_ids(self, include_self=True):
        ids = [i.id for i in self.get_descendants() if i.is_active]
        if include_self:
            ids.append(self.id)
        return ids

    def get_workers(self, is_active=None):
        subs = self.get_sub_department_ids()
        qset = self.party.workers.filter(departments__id__in=subs)
        if is_active is not None:
            qset = qset.filter(is_active)
        return qset

    def get_or_create_department_by_path(self, path):
        parent = self
        for d in path.split("/"):
            parent, created = parent.sub_departments.get_or_create(parent=parent, name=d)
        return parent, created

    @cached_property
    def path(self):
        return "/".join([a.name for a in self.get_ancestors()] + [self.name])

    @cached_property
    def active_workers_count(self):
        return self.get_workers(is_active=True).count()


class Worker(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "成员"
        unique_together = ('party', 'number')
        permissions = (
            ("view_worker", "查看成员资料"),
        )

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="workers")
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True, blank=True,
                                related_name="as_saas_worker")
    number = models.CharField("编号", max_length=64, db_index=True)
    name = models.CharField("名字", max_length=64, db_index=True)
    departments = models.ManyToManyField(Department, verbose_name=Department._meta.verbose_name, blank=True,
                                         related_name="workers")
    position = models.CharField("职位", max_length=64, null=True, blank=True)
    # status = models.SmallIntegerField("状态", choices=choices.CHOICE_WORKER_STATUS,
    #                                   default=choices.WORKER_STATUS_WORKING)
    is_active = models.BooleanField("有效", default=True)
    entrance_date = models.DateField(u'加入日期', null=True, blank=True)
    quit_date = models.DateField(u'退出日期', null=True, blank=True)
    profile = modelutils.KeyValueJsonField("档案", null=True, blank=True)
    settings = GenericRelation("common.Setting")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return self.name

    def _auto_create_user(self):
        if not self.user:
            import unidecode
            uid = unidecode.unidecode(self.name).replace(" ", "").lower()
            sid = 1
            org = self.party.slug
            number = uid
            while User.objects.filter(username="%s@%s" % (number, org)).exists():
                sid += 1
                number = "%s%s" % (uid, sid)
            self.user = User.objects.create_user(username="%s@%s" % (number, org), first_name=self.name)
            self.user.save()

    def _auto_deactivated(self):
        # is_active = self.status != choices.WORKER_STATUS_QUIT
        if self.is_active != self.user.is_active:
            self.user.is_active = self.is_active
            self.user.save()

    def save(self, **kwargs):
        from django.db import transaction

        self.name = self.name.replace(" ", "")
        with transaction.atomic():
            self._auto_create_user()
            self._auto_deactivated()
            if not self.number:
                self.number = self.user.username.split("@")[0]
            super(Worker, self).save(**kwargs)


class App(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "应用"
        unique_together = ('party', 'name')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="apps")
    name = models.CharField("名字", max_length=64, db_index=True)
    status = models.PositiveSmallIntegerField("状态", choices=choices.CHOICES_APP_STATUS,
                                              default=choices.APP_STATUS_INSTALL)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return "%s install %s" % (self.party, self.name)
