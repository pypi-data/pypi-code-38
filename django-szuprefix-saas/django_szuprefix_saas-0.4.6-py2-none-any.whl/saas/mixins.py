# -*- coding:utf-8 -*-
__author__ = 'denishuang'

from django.forms import ModelChoiceField
from rest_framework.relations import RelatedField

from django_szuprefix.api.mixins import RestCreateMixin

from . import permissions


class PartyMixin(RestCreateMixin):
    # permission_classes = [permissions.IsSaasWorker] + super.permission_classes

    # def initial(self, request, *args, **kwargs):
    #     super(PartyMixin, self).initial(request, *args, **kwargs)
    #     self.worker = request.user.as_saas_worker
    #     self.party = self.worker.party

    def get_permissions(self):
        return [permissions.IsSaasWorker()] + super(PartyMixin, self).get_permissions()

    def get_queryset(self):
        return super(PartyMixin, self).get_queryset().filter(party=self.party)

    def get_form_kwargs(self):
        r = super(PartyMixin, self).get_form_kwargs()
        r['party'] = self.party
        return r

    def get_serializer(self, *args, **kwargs):
        kwargs['party'] = self.party
        return super(PartyMixin, self).get_serializer(*args, **kwargs)


class SubdomainSerializerMixin(object):
    subdomain_fields = []

    def __init__(self, *args, **kwargs):
        for f in self.subdomain_fields:
            if f in kwargs:
                setattr(self, f, kwargs.pop(f))
        super(SubdomainSerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def addFilter2RelativeFields(self):
        if not self.subdomain_fields:
            return
        for n, f in self.fields.iteritems():
            model = f.queryset.model
            if isinstance(f, (RelatedField, ModelChoiceField)):
                d = dict([(sf, getattr(self, sf)) for sf in self.subdomain_fields if hasattr(model, sf)])
                if d:
                    f.queryset = f.queryset.filter(**d)


class PartyFormMixin(object):
    party = None

    def __init__(self, *args, **kwargs):
        if 'party' in kwargs:
            self.party = kwargs.pop('party')
        super(PartyFormMixin, self).__init__(*args, **kwargs)
        self.addFilter2ModelChoiceFields()

    def addFilter2ModelChoiceFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, ModelChoiceField) and f.queryset and hasattr(f.queryset.model, 'party'):
                f.queryset = f.queryset.filter(party=self.party)

    def save(self, commit=True):
        self.instance.party = self.party
        return super(PartyFormMixin, self).save(commit)


class PartySerializerMixin(object):
    party = None

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data')
        if 'party' in kwargs:
            self.party = kwargs.pop('party')
            # data['party'] = self.party.id
            # print data
        super(PartySerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def to_internal_value(self, value):
        d = super(PartySerializerMixin, self).to_internal_value(value)
        d['party'] = self.party
        return d

    def addFilter2RelativeFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, RelatedField) and f.queryset and hasattr(f.queryset.model, 'party'):
                f.queryset = f.queryset.filter(party=self.party)

    def save(self, **kwargs):
        kwargs["party"] = self.party
        return super(PartySerializerMixin, self).save(**kwargs)


class UserSerializerMixin(object):
    user = None

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(UserSerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def addFilter2RelativeFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, RelatedField) and hasattr(f.queryset.model, 'user'):
                f.queryset = f.queryset.filter(user=self.user)
