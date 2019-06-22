from django.db import models
from mint import mixins
from mint import exceptions
from mint import serializer
from django.http import QueryDict
import json


class EmptyModel(models.Model):
    class Meta:
        app_label = '_mint'


class Controller(mixins.ListMixin, mixins.DetailMixin, mixins.FieldMixin):
    model = EmptyModel
    serializer = serializer.Serializer

    max_limit = None

    def __init__(self, request):
        self.request = request
        self.original_model = self.model
        self.args = {}
        self.limit = None
        self.offset = None
        self.open_args()
        self.open_limit_and_offset()
        self.serializer_instance = self.serializer(self)

    def open_model(self, idx=None):
        if idx:
            try:
                self.model = self.model.objects.get(pk=idx)
            except self.model.DoesNotExist:
                raise exceptions.HttpNotFound("Could not find %s with id %d" % (self.__class__.__name__, int(idx)))
        else:
            self.model = self.model.objects.all()

    def open_args(self):
        if self.request.method == 'GET':
            self.args = self.request.GET.dict()
        elif self.request.method == 'POST':
            if 'CONTENT_TYPE' in self.request.META and 'application/json' in self.request.META['CONTENT_TYPE']:
                if len(self.request.body) > 0:
                    self.args = json.loads(self.request.body.decode('utf-8'))
            else:
                self.args = self.request.POST.dict()
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            if 'CONTENT_TYPE' in self.request.META and 'application/json' in self.request.META['CONTENT_TYPE']:
                if len(self.request.body) > 0:
                    self.args = json.loads(self.request.body.decode('utf-8'))
            else:
                self.args = QueryDict(self.request.body).dict()

    def open_limit_and_offset(self):
        if 'limit' in self.args:
            self.limit = int(self.args['limit'])
        if self.limit and self.max_limit and self.limit > self.max_limit:
            self.limit = self.max_limit
        elif self.max_limit and not self.limit:
            self.limit = self.max_limit
        self.offset = int(self.args.get('offset', 0))

    def has_action(self, action):
        return hasattr(self, action)

    def exec_root(self):
        if self.request.method not in self._list_methods():
            raise exceptions.HttpNotAllowed("Invalid method (%s) for this controller (%s)."
                                            % (self.request.method, self.__class__.__name__))
        return self._list_methods()[self.request.method]()

    def exec_id(self, idx):
        if self.request.method not in self._detail_methods():
            raise exceptions.HttpNotAllowed("Invalid method (%s) for this controller (%s)."
                                            % (self.request.method, self.__class__.__name__))
        self.open_model(idx)
        return self._detail_methods()[self.request.method]()

    def exec_action(self, action, idx=None):
        if not hasattr(self, action):
            raise exceptions.HttpNotAllowed("Invalid action (%s) for this controller (%s)."
                                            % (action, self.__class__.__name__))
        if idx:
            self.open_model(idx)
        return getattr(self, action)()