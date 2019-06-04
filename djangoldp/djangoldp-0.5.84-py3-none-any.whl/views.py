from django.apps import apps
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.core.urlresolvers import get_resolver
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404
from django.utils.decorators import classonlymethod
from guardian.shortcuts import get_objects_for_user
from pyld import jsonld
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet

from djangoldp.models import LDPSource, Model
from .serializers import LDPSerializer


class JSONLDRenderer(JSONRenderer):
    media_type = 'application/ld+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is not None:
            data["@context"] = settings.LDP_RDF_CONTEXT
        return super(JSONLDRenderer, self).render(data, accepted_media_type, renderer_context)


class JSONLDParser(JSONParser):
    media_type = 'application/ld+json'

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JSONLDParser, self).parse(stream, media_type, parser_context)
        return jsonld.compact(data, ctx=settings.LDP_RDF_CONTEXT)


class NoCSRFAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class LDPViewSetGenerator(ModelViewSet):
    """An extension of ModelViewSet that generates automatically URLs for the model"""
    model = None
    nested_fields = []
    model_prefix = None
    list_actions = {'get': 'list', 'post': 'create'}
    detail_actions = {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}

    @classonlymethod
    def get_model(cls, **kwargs):
        '''gets the model in the arguments or in the viewset definition'''
        model = kwargs.get('model') or cls.model
        if isinstance(model, str):
            model = apps.get_model(model)
        return model

    @classonlymethod
    def get_lookup_arg(cls, **kwargs):
        return kwargs.get('lookup_url_kwarg') or cls.lookup_url_kwarg or kwargs.get('lookup_field') or cls.lookup_field

    @classonlymethod
    def get_detail_expr(cls, lookup_field=None, **kwargs):
        '''builds the detail url based on the lookup_field'''
        lookup_field = lookup_field or cls.get_lookup_arg(**kwargs)
        lookup_group = r'\d' if lookup_field == 'pk' else r'[\w\-\.]'
        return r'(?P<{}>{}+)/'.format(lookup_field, lookup_group)

    @classonlymethod
    def urls(cls, **kwargs):
        kwargs['model'] = cls.get_model(**kwargs)
        model_name = kwargs['model']._meta.object_name.lower()
        if kwargs.get('model_prefix'):
            model_name = '{}-{}'.format(kwargs['model_prefix'], model_name)
        detail_expr = cls.get_detail_expr(**kwargs)

        urls = [
            url('^$', cls.as_view(cls.list_actions, **kwargs), name='{}-list'.format(model_name)),
            url('^' + detail_expr + '$', cls.as_view(cls.detail_actions, **kwargs),
                name='{}-detail'.format(model_name)),
        ]

        for field in kwargs.get('nested_fields') or cls.nested_fields:
            urls.append(url('^' + detail_expr + field + '/', LDPNestedViewSet.nested_urls(field, **kwargs)))

        return include(urls)


class LDPViewSet(LDPViewSetGenerator):
    """An automatically generated viewset that serves models following the Linked Data Platform convention"""
    fields = None
    exclude = None
    depth = 2
    many_depth = 1
    renderer_classes = (JSONLDRenderer,)
    parser_classes = (JSONLDParser,)
    authentication_classes = (NoCSRFAuthentication,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permission_classes:
            for p in self.permission_classes:
                if hasattr(p, 'filter_class') and p.filter_class:
                    self.filter_backends = p.filter_class

        self.serializer_class = self.build_serializer()

    def build_serializer(self):
        model_name = self.model._meta.object_name.lower()
        lookup_field = get_resolver().reverse_dict[model_name + '-detail'][0][0][1][0]
        meta_args = {'model': self.model, 'extra_kwargs': {
            '@id': {'lookup_field': lookup_field}},
                     'depth': self.depth,
                     'extra_fields': self.nested_fields}
        if self.fields:
            meta_args['fields'] = self.fields
        else:
            meta_args['exclude'] = self.exclude or ()
        meta_class = type('Meta', (), meta_args)
        return type(LDPSerializer)(model_name + 'Serializer', (LDPSerializer,), {'Meta': meta_class})

    def perform_create(self, serializer, **kwargs):
        if hasattr(self.model._meta, 'auto_author') and isinstance(self.request.user, get_user_model()):
            kwargs[self.model._meta.auto_author] = self.request.user
        serializer.save(**kwargs)

    def get_queryset(self, *args, **kwargs):
        if self.model:
            return self.model.objects.all()
            perm = "view_{}".format(self.model._meta.model_name.lower())
            return get_objects_for_user(self.request.user, perm, klass=self.model)
        else:
            return super(LDPView, self).get_queryset(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        response = super(LDPViewSet, self).dispatch(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN')
        response["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE"
        response["Access-Control-Allow-Headers"] = "authorization, Content-Type, if-match, accept"
        response["Access-Control-Expose-Headers"] = "Location"
        response["Access-Control-Allow-Credentials"] = 'true'
        response["Accept-Post"] = "application/ld+json"
        if response.status_code in [201, 200] and '@id' in response.data:
            response["Location"] = response.data['@id']
        else:
            pass
        response["Accept-Post"] = "application/ld+json"
        if request.user.is_authenticated():
            try:
                response['User'] = request.user.webid()
            except AttributeError:
                pass
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return response


class LDPNestedViewSet(LDPViewSet):
    """
    A special case of LDPViewSet serving objects of a relation of a given object
    (e.g. members of a group, or skills of a user)
    """
    parent_model = None
    parent_lookup_field = None
    related_field = None
    nested_field = None
    nested_related_name = None

    def get_parent(self):
        return get_object_or_404(self.parent_model, **{self.parent_lookup_field: self.kwargs[self.parent_lookup_field]})

    def perform_create(self, serializer, **kwargs):
        kwargs[self.nested_related_name] = self.get_parent()
        super().perform_create(serializer, **kwargs)

    def get_queryset(self, *args, **kwargs):
        if self.related_field.many_to_many or self.related_field.one_to_many:
            return getattr(self.get_parent(), self.nested_field).all()
        if self.related_field.many_to_one or self.related_field.one_to_one:
            return [getattr(self.get_parent(), self.nested_field)]

    @classonlymethod
    def get_related_fields(cls, model):
        return {field.get_accessor_name(): field for field in model._meta.fields_map.values()}

    @classonlymethod
    def nested_urls(cls, nested_field, **kwargs):
        try:
            related_field = cls.get_model(**kwargs)._meta.get_field(nested_field)
        except FieldDoesNotExist:
            related_field = cls.get_related_fields(cls.get_model(**kwargs))[nested_field]
        if related_field.related_query_name:
            nested_related_name = related_field.related_query_name()
        else:
            nested_related_name = related_field.remote_field.name

        return cls.urls(
            model=related_field.related_model,
            exclude=(nested_related_name,) if related_field.one_to_many else (),
            parent_model=cls.get_model(**kwargs),
            nested_field=nested_field,
            nested_related_name=nested_related_name,
            related_field=related_field,
            parent_lookup_field=cls.get_lookup_arg(**kwargs),
            model_prefix=cls.get_model(**kwargs)._meta.object_name.lower(),
            permission_classes=Model.get_permission_classes(related_field.related_model,
                                                            kwargs.get('permission_classes', ())),
            lookup_url_kwarg=related_field.related_model._meta.object_name.lower() + '_id')


class LDPSourceViewSet(LDPViewSet):
    model = LDPSource
    federation = None

    @classonlymethod
    def urls(cls, **kwargs):
        try:
            return include([url(name + '/', super(LDPSourceViewSet, cls).urls(federation=name, **kwargs))
                            for name in LDPSource.objects.order_by().values_list('federation', flat=True).distinct()])
        except (OperationalError, ProgrammingError):  # for the case where the table doesn't exist
            return include([])

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(federation=self.federation)
