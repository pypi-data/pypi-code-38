from api.authorisation import AuthBundle
from api.decorators import jsonapi
from api.exceptions import (
    MethodNotAllowedError, ForbiddenError, ConfigurationError,
    UnprocessableEntityError, BadRequestError
)

from api.filtering import qs_name_to_kwarg
from api.mixins import (
    ModelMixin,
    JSONMixin,
    AuthenticationMixin,
    AuthorisationMixin
)

from api.utils import (
    get_id_field,
    get_object_id,
    get_type_name,
    unurlise_field_name
)

from api import settings
from django.core.exceptions import FieldError, FieldDoesNotExist
from django.db import transaction
from django.db.models import ForeignKey, ManyToOneRel, ManyToManyField
from django.http.response import HttpResponse
from django.views.generic.base import View
import re


class ModelViewBase(
    ModelMixin,
    JSONMixin,
    AuthenticationMixin,
    AuthorisationMixin,
    View
):
    """
    View mixin that provides common functionality between all the various
    views that make up a Django model's API nedpoint.
    """

    def apply_filter(self, key, value):
        """
        Takes a JSON-API-specified field name and returns a dictionary
        representing part of a Django model query. Override this method to
        provide custom, or more complex filtering.
        """

        f = qs_name_to_kwarg(key, self.model._meta)

        return {
            f: value
        }

    def get_filter(self):
        """
        This method looks for querystring parameters that follow the
        `filter[<field>]` pattern, and atetmpts to turn the filter expression
        into a Django query expression, expressed as a dictionary that can
        then be applied via a Django query's kwargs.
        """

        kwargs = {}

        for key in self.request.GET.keys():
            match = re.match(r'^filter\[([\w\.-]+)\]$', key)
            if match is None:
                continue

            for field in match.groups():
                applied = self.apply_filter(field, self.request.GET[key])
                if any(applied):
                    kwargs.update(applied)

        return kwargs

    def get_include(self):
        """
        Given a request with an `include` querystring parameter, returns a
        list of model field names that can be found in that list. If a field
        has been requested that can't be found, an `UnprocessableEntityError`
        exception is raised.
        """

        includes = []

        for name in [
            name.strip()
            for name in self.request.GET.get('include', '').split(',')
            if name and name.strip()
        ]:
            try:
                field = self.model._meta.get_field(
                    unurlise_field_name(name)
                )
            except FieldError as ex:
                raise UnprocessableEntityError(str(ex))
            except FieldDoesNotExist:
                raise BadRequestError(
                    'Relationship "%s" does not exist.' % name
                )
            else:
                includes.append(field.name)

        return includes

    def get_order_by(self):
        """
        If specified by querystring, this method returns the field names
        requested. If an `order_by` property is declared, this is used as a
        fallback, and finally if no ordering can be determined, the field used
        as the identifier (usually teh primary key field) is returned.
        """

        if self.request.GET.get('sort'):
            sort = [
                s.strip().replace('.', '__')
                for s in self.request.GET['sort'].split(',')
                if s and s.strip()
            ]

            if any(sort):
                return tuple(set(sort))

        return getattr(self, 'order_by', [])

    def get_paginate_by(self):
        """
        Returns the number of records that should be in a paginated list.
        If a `paginate_by` property is specified, its value is used, otherwise
        it's taken from the default `API_DEFAULT_RPP` setting.
        """

        return self.request.GET.get('limit') or getattr(
            self,
            'paginate_by',
            settings.DEFAULT_RPP
        )

    def get_auth_bundle_data(self):
        """
        Returns a dictionary of data used to construct an
        :class:`~authorisation.AuthBundle` object.
        """

        return {}

    def get_auth_bundle(self, context):
        """
        Returns an :class:`~authorisation.AuthBundle` object.

        :param context: The current view context ('list' or 'dateil').
        :type context: str
        """

        return AuthBundle(context, **self.get_auth_bundle_data())

    def precheck(self, request, context):
        """
        Performs common preflight checks, like ensuring the requested HTTP
        method is supported by the view, and that the operation can be
        performed by the current user.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        :param context: The current view context ('list' or 'dateil').
        :type context: str
        """

        from django.contrib.auth.models import AnonymousUser

        method = request.method.lower()
        if method == 'head':
            method = 'get'

        if not hasattr(self, method):
            raise MethodNotAllowedError('Method not allowed.')

        authenticated = False
        for authenticator in self.get_authenticators():
            if authenticator.authenticate(request) is True:
                authenticated = True
                break

        if not authenticated:
            request.user = AnonymousUser()

        request.bundle = self.get_auth_bundle(context)
        for authoriser in self.get_authorisers():
            if authoriser.authorise(request, request.bundle) is True:
                return

        raise ForbiddenError('Operation not permitted.')

    def form_valid(self, form):
        """
        This method is run when a Django form has been validated, and is ready
        to have its data saved.

        :param form: The form that has been validated.
        :type form: ``django.forms.Form``
        """

        resource = self.get_resource()
        return resource.form_valid(form)


class ListView(ModelViewBase):
    def get_auth_bundle_data(self):
        """
        Returns a dictionary of data used to construct an
        :class:`~authorisation.AuthBundle` object. Inlcudes an `object`
        key which represents the Django model object the user wants to
        interact with.
        """

        data = super().get_auth_bundle_data()
        obj = self.get_resource()
        data['model'] = obj.model

        return data

    @jsonapi()
    def dispatch(self, request, *args, **kwargs):
        """
        Performs the necessary HTTP method and returns the response in JSON
        format. In the case of a POST, the ``Location`` header is set to the
        object's ``links.self`` property, in accordance with JSON API
        recommendations.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        if request.method in ('HEAD', 'GET'):
            self.precheck(request, 'list')

            return self.respond(
                self.get(request)
            )

        with transaction.atomic():
            self.precheck(request, 'list')
            if request.method == 'POST':
                data = self.post(request)
                response = self.respond(data)

                if response.status_code == 200:
                    response.status_code = 201
                    response['Location'] = data['links']['self'].resolve(request)

                return response

    def get_resource_kwargs(self):
        """
        This method returns the keyword arguments necessary to instantiate
        a model reosurce object.
        """

        filter = self.get_filter()
        include = self.get_include()
        order_by = self.get_order_by()
        paginate_by = self.get_paginate_by()
        kwargs = {}

        if any(filter):
            kwargs['filter'] = filter

        if any(include):
            kwargs['include'] = include

        if any(order_by):
            kwargs['order_by'] = order_by

        if paginate_by is not None:
            kwargs['paginate_by'] = paginate_by
            kwargs['page'] = self.request.GET.get('page', '1')

        if self.request.method == 'POST':
            kwargs['select_for_update'] = True

        return kwargs

    def get(self, request):
        """
        Retrieves the required resource object list and packs it.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        return self.get_resource().pack()

    @transaction.atomic()
    def post(self, request):
        """
        Creates a new Django model instance using the list resource, validates
        it and returns the object packed by the detail resource.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        from api.resources import registry

        data = self.deserialise(request.body)
        resource = self.get_resource()
        unpacked, extra = resource.unpack(data)
        form = resource.get_form(data=unpacked)
        self.patch_form_fields(form)

        if not form.is_valid():
            raise UnprocessableEntityError(
                'Object did not validate.',
                form.errors
            )

        obj = self.form_valid(form)
        resource_class = registry.get(type(obj), 'detail')
        resource = resource_class(object=obj)
        resource.save_extra(extra)
        return resource.pack()


class DetailView(ModelViewBase):
    @jsonapi()
    def dispatch(self, request, *args, **kwargs):
        """
        Performs the necessary HTTP method and returns the response in JSON
        format.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        if request.method in ('HEAD', 'GET'):
            self.precheck(request, 'detail')
            return self.respond(
                self.get(request)
            )

        with transaction.atomic():
            self.precheck(request, 'detail')
            if request.method == 'PATCH':
                return self.respond(
                    self.patch(request)
                )

            if request.method == 'PUT':
                return self.respond(
                    self.put(request)
                )

            if request.method == 'DELETE':
                return self.delete(request)

    def get_resource_kwargs(self):
        """
        This method returns the keyword arguments necessary to instantiate
        a model reosurce object.
        """

        include = self.get_include()
        kwargs = {
            'object_kwargs': self.kwargs
        }

        if any(include):
            kwargs['include'] = include

        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            kwargs['select_for_update'] = True

        return kwargs

    def get_auth_bundle_data(self):
        """
        Returns a dictionary of data used to construct an
        :class:`~authorisation.AuthBundle` object. Inlcudes an `object`
        key which represents the Django model object the user wants to
        interact with.
        """

        data = super().get_auth_bundle_data()
        obj = self.get_resource().get_object()
        data['object'] = obj
        data['model'] = type(obj)

        return data

    def get(self, request, **kwargs):
        """
        Retrieves the required resource object and packs it.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        return self.get_resource().pack()

    def patch(self, request):
        """
        Performs an update on a Django model instance. Unlike a PUT operation,
        a PATCH may contain partial data, so only the data supplied in the JSON
        object must be updated. Once validated and saved, the method returns
        the updated object.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        data = self.deserialise(request.body)
        resource = self.get_resource()
        unpacked, extra = resource.unpack(dict(**data))

        form_class = resource.get_form_class(fields=unpacked.keys())
        kw = resource.get_form_kwargs(form_class)
        kw['instance'] = resource.get_object()
        kw['data'] = unpacked
        form = form_class(**kw)
        self.patch_form_fields(form)

        if not form.is_valid():
            raise UnprocessableEntityError(
                'Object did not validate.',
                form.errors
            )

        resource.object = self.form_valid(form)
        resource.save_extra(extra)
        return resource.pack()

    def put(self, request):
        """
        Performs a full-object update of a Django model instance, and returns
        the updated object.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        data = self.deserialise(request.body)
        resource = self.get_resource()
        unpacked, extra = resource.unpack(dict(**data))
        form = resource.get_form(
            data=unpacked,
            instance=resource.get_object()
        )

        self.patch_form_fields(form)

        if not form.is_valid():
            raise UnprocessableEntityError(
                'Object did not validate.',
                form.errors
            )

        resource.object = self.form_valid(form)
        resource.save_extra(extra)
        return resource.pack()

    def delete(self, request):
        """
        Performs deletion of a Django model instance, and returns an empty 204
        response indicating that the operation was successul and the content
        has disappeared.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        self.get_resource().get_object().delete()
        return HttpResponse(
            status=204,
            content_type='application/vnd.api+json'
        )


class RelationView(ModelViewBase):
    def get_resource_kwargs(self):
        """
        This method returns the keyword arguments necessary to instantiate
        a model reosurce object. Here, an `object_kwargs` key is added, which
        instructs the detail resource object how to find the specific Django
        model instance the user wants to interact with.
        """

        include = self.get_include()
        kwargs = {
            'object_kwargs': self.kwargs
        }

        if any(include):
            kwargs['include'] = include

        return kwargs

    @jsonapi()
    def get(self, request, **kwargs):
        """
        Retrieves the required object relation and packs it. In the case of
        many-to-many or many-to-one relationships, a full list of objects is
        packed; otherwise just the single related object is packed.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        from api.resources import registry

        self.precheck(request, 'detail')
        resource = self.get_resource()
        obj = resource.get_object()
        field = self.model._meta.get_field(self.rel)

        if field is None:  # pragma: no cover
            raise ConfigurationError(
                '\'%s\' field not found in \'%s.%s\' model' % (
                    self.rel,
                    self.model._meta.app_label,
                    self.model._meta.model_name
                )
            )

        if isinstance(field, (ManyToOneRel, ManyToManyField)):
            context = 'list'
            subresource_kwargs = {
                'filter': {
                    'pk__in': getattr(obj, field.name).values_list(
                        'pk',
                        flat=True
                    )
                }
            }
        else:
            context = 'detail'
            subresource_kwargs = {
                'object_kwargs': {
                    'pk': field.value_from_object(obj)
                }
            }

        subresource_class = registry.get(
            field.related_model,
            context
        )

        subresource = subresource_class(**subresource_kwargs)

        return self.respond(
            subresource.pack()
        )


class RelationshipView(ModelViewBase):
    def get_resource_kwargs(self):
        """
        This method returns the keyword arguments necessary to instantiate
        a model reosurce object. Here, an `object_kwargs` key is added, which
        instructs the detail resource object how to find the specific Django
        model instance the user wants to interact with.
        """

        include = self.get_include()
        kwargs = {
            'object_kwargs': self.kwargs
        }

        if any(include):
            kwargs['include'] = include

        return kwargs

    @jsonapi()
    def get(self, request, **kwargs):
        """
        Retrieves the required object relation and packs it. In the case of
        many-to-many or many-to-one relationships, a list of object IDs and
        types is packed; otherwise just the single related object ID and type
        is packed.

        :param request: The HTTP request.
        :type request: ``django.http.request.HttpRequest``
        """

        self.precheck(request, 'detail')

        resource = self.get_resource()
        obj = resource.get_object()
        field = self.model._meta.get_field(self.rel)

        if field is None:  # pragma: no cover
            raise ConfigurationError(
                '\'%s\' field not found in \'%s.%s\' model' % (
                    self.rel,
                    self.model._meta.app_label,
                    self.model._meta.model_name
                )
            )

        subobj = getattr(obj, field.name)
        if isinstance(field, ForeignKey):
            data = {
                'id': get_object_id(subobj),
                'type': get_type_name(subobj)
            }
        elif isinstance(field, (ManyToOneRel, ManyToManyField)):
            type_name = get_type_name(field.related_model)
            data = [
                {
                    'id': pk,
                    'type': type_name
                } for pk in subobj.values_list(
                    get_id_field(field.related_model),
                    flat=True
                )
            ]
        else:  # pragma: no cover
            raise ConfigurationError('Unsupported relationship')

        rel_url = resource.link(obj)
        packed = {
            'links': {
                'self': self.request.build_absolute_uri()
            },
            'data': data
        }

        if rel_url:
            packed['links']['related'] = rel_url

        return self.respond(packed)


def modelmixin_factory(
    Model, prepopulated_fields={}, queryset=None,
    authenticators=None, authorisers=None
):
    """
    A factory function for creating a model view mixin in realtime.

    :param Model: The model to create the mixin for.
    :type Model: ``django.db.models.Model``

    :param prepopulated_fields:
        (optional) Fields that should be prepopulated by the API. For example:
        ``{'creator': lambda r: r.user}``, where `r` represents the current
        request.
    :type prepopulated_fields: dict

    :param queryset:
        (optional) A function, called with the current HTTP request, that can
        be used to override the default queryset.
    :type queryset: lambda, func

    :param authenticators:
        (optional) A list of authenticators specific to this API endpoint.
    :type authenticators: list, tuple

    :param authorisers:
        (optional) A list of authorisers specific to this API endpoint.
    :type authorisers: list, tuple
    """

    opts = Model._meta
    attrs = {
        'model': Model
    }

    if authenticators is not None:
        attrs['authenticators'] = authenticators

    if authorisers is not None:
        attrs['authorisers'] = authorisers

    class mixin(object):
        def get_resource_kwargs(self):
            kwargs = super().get_resource_kwargs()

            if queryset is not None:
                kwargs['queryset'] = queryset(self.request)

            return kwargs

        def form_valid(self, form):
            if self.request.method in ('PUT', 'PATCH') or not any(
                prepopulated_fields
            ):
                return super().form_valid(form)

            obj = form.save(commit=False)
            for key, expression in prepopulated_fields.items():
                if opts.get_field(key) is None:  # pragma: no cover
                    raise ConfigurationError(
                        '\'%s\' field not present in %s model' % (
                            key,
                            opts.model_name
                        )
                    )

                value = expression(self.request)
                setattr(obj, key, value)

            obj.save()
            form.save_m2m()

            return obj

    return type(
        '%sMixin' % Model.__name__,
        (mixin,),
        attrs
    )


def relationmixin_factory(ParenetModel, name):
    """
    A factory function for creating a relation view mixin in realtime.

    :param ParenetModel: The parent model to create the mixin for.
    :type ParenetModel: ``django.db.models.Model``

    :param name:
        The name of the within the ``ParentModel`` to lookup. Must be some kind
        of relationship field.
    :type name: str
    """

    attrs = {
        'model': ParenetModel,
        'rel': name
    }

    return type(
        '%sRelationMixin' % ParenetModel.__name__,
        (),
        attrs
    )


def relationshipmixin_factory(ParenetModel, name):
    """
    A factory function for creating a relationship view mixin in realtime.

    :param ParenetModel: The parent model to create the mixin for.
    :type ParenetModel: ``django.db.models.Model``

    :param name:
        The name of the within the ``ParentModel`` to lookup. Must be some kind
        of relationship field.
    :type name: str
    """

    attrs = {
        'model': ParenetModel,
        'rel': name
    }

    return type(
        '%sRelationshipMixin' % ParenetModel.__name__,
        (),
        attrs
    )
