def rest(resource, **kwargs):
    """
    Creates model list and detail resources, and API endpoints to interact with
    them.

    :param resource:
        The Django model to create a REST interface for, or the
        resource to use when creating the endpoints.
    :type resource: ``django.db.models.Model``, :class:`~resources.ModelResource`

    :param fields:
        (optional) A list of field names to include in resource objects.
    :type fields: list, tuple

    :param exclude:
        (optional) A list of field names to exclude from resource objects.
    :type exclude: list, tuple

    :param readonly_fields:
        (optional) Names of fields that are not updateable via the API.
    :type readonly_fields: list, tuple

    :param prepopulated_fields:
        (optional) A dictionary of fields with lamba expressions for setting model
        properties (lke setting the current user as the creator of an object).
    :type prepopulated_fields: dict

    :param form_class: (optional) Overrides the factory-generated model form
    :type form_class: `django.forms.ModelForm`

    :param queryset: (optional) A replacement for the default queryset
    :type queryset: lambda, func

    :param order_by: (optional) A list of field names to order the objects by.
    :type order_by: list, tuple

    :param pk_field: (optional) The primary key field name.
    :type pk_field: str

    :param paginate_by:
        (optional) The number of items to return in a paginated list. (Defaults
        to the value of ``settings.API_DEFAULT_RPP``.)
    :type paginate_by: int

    :param relations:
        (optional) A list of many-to-many or many-to-one relationships that
        need to be represented in the API.
    :type relations: list, tuple

    :param authenticators:
        (optional) Override the default authenticators for this endpoint.
        (Defaults to the value of ``settings.API_DEFAULT_AUTHENTICATORS``.)
    :type authenticators: list, tuple

    :param authorisers:
        (optional) Override the default authorisers for this endpoint.
        (Defaults to the value of ``settings.API_DEFAULT_AUTHORISERS``.)
    :type authorisers: list, tuple
    """

    from api.resources import registry, ModelResource
    from api.exceptions import ConfigurationError
    from api.utils import get_type_name, urlise_field_name
    from api.views.models import (
        modelmixin_factory, ListView, DetailView,
        relationmixin_factory, relationshipmixin_factory,
        RelationView, RelationshipView
    )

    from django.conf.urls import url
    from django.db.models.base import ModelBase
    from django.views.decorators.csrf import csrf_exempt

    queryset = kwargs.pop('queryset', None)
    order_by = kwargs.pop('order_by', None)
    fields = kwargs.pop('fields', None)
    exclude = kwargs.pop('exclude', None)
    readonly_fields = kwargs.pop('readonly_fields', None)
    form_class = kwargs.pop('form_class', None)
    prepopulated_fields = kwargs.pop('prepopulated_fields', None)
    pk_field = kwargs.pop('pk_field', None)
    paginate_by = kwargs.pop('paginate_by', None)
    relations = kwargs.pop('relations', ())
    authorisers = kwargs.pop('authorisers', None)
    authenticators = kwargs.pop('authenticators', None)

    if isinstance(resource, ModelBase):
        opts = resource._meta
        slug = get_type_name(resource)

        for key in kwargs.keys():  # pragma: no cover
            raise TypeError(
                'rest() got an unexpected keyword argument \'%s\'' % key
            )

        kw = {
            'relationships': sorted(list(relations))
        }

        if queryset is not None:
            kw['queryset'] = queryset

        if order_by is not None:
            kw['order_by'] = order_by

        if fields is not None:
            kw['fields'] = fields

        if exclude is not None:
            kw['exclude'] = exclude

        if readonly_fields is not None:
            kw['readonly_fields'] = readonly_fields

        if form_class is not None:
            kw['form_class'] = form_class

        if pk_field is not None:
            kw['pk_field'] = pk_field

        if paginate_by is not None:
            kw['paginate_by'] = paginate_by

        list_resource, detail_resource = registry.register(resource, **kw)
    elif issubclass(resource, ModelResource):
        list_resource = registry.get(resource.model, 'list')
        detail_resource = resource

        opts = resource.model._meta
        slug = get_type_name(resource.model)
    else:  # pragma: no cover
        raise ConfigurationError(
            'resource argument must be a Django model or ModelResource, '
            'not \'%s\'' % type(resource)
        )

    kw = {}

    urlpatterns = []
    if queryset is not None:
        kw['queryset'] = queryset

    if prepopulated_fields is not None:
        kw['prepopulated_fields'] = prepopulated_fields

    if authenticators is not None:
        kw['authenticators'] = authenticators

    if authorisers is not None:
        kw['authorisers'] = authorisers

    mixin = modelmixin_factory(list_resource.model, **kw)

    list_view = type(
        '%sListView' % list_resource.model.__name__,
        (mixin, ListView),
        {
            'resource_class': list_resource
        }
    )

    detail_view = type(
        '%sDetailView' % list_resource.model.__name__,
        (mixin, DetailView),
        {
            'resource_class': detail_resource
        }
    )

    urlpatterns.append(
        url(
            '^' + slug + '/$',
            csrf_exempt(list_view.as_view()),
            name='%s_%s_list' % (
                opts.app_label,
                opts.model_name
            )
        )
    )

    urlpatterns.append(
        url(
            (
                '^' + slug + ''
                '/(?P<' + (pk_field or 'pk') + '>[^/]+)/$'
            ),
            csrf_exempt(detail_view.as_view()),
            name='%s_%s_detail' % (
                opts.app_label,
                opts.model_name
            )
        )
    )

    for rel_name in getattr(detail_resource, 'relationships', relations):
        rel_field = opts.get_field(rel_name)
        if rel_field is None:  # pragma: no cover
            raise ConfigurationError(
                '\'%s\' field not present in %s model' % (
                    key,
                    opts.model_name
                )
            )

        rel_slug = rel_field.name

        relation_mixin = relationmixin_factory(
            list_resource.model,
            rel_field.name
        )

        relationship_mixin = relationshipmixin_factory(
            list_resource.model,
            rel_field.name
        )

        relation_view = type(
            '%s%sRelationView' % (
                (
                    list_resource.model.__name__,
                    rel_slug.replace('_', ' ').title().replace(' ', '')
                )
            ),
            (relation_mixin, RelationView),
            {
                'resource_class': detail_resource
            }
        )

        relationship_view = type(
            '%s%sRelationshipView' % (
                (
                    list_resource.model.__name__,
                    rel_slug.replace('_', ' ').title().replace(' ', '')
                )
            ),
            (relationship_mixin, RelationshipView),
            {
                'resource_class': detail_resource
            }
        )

        urlpatterns.append(
            url(
                (
                    '^' + slug + '/'
                    '(?P<' + (pk_field or 'pk') + '>[^/]+)/'
                    'relationships/' + urlise_field_name(rel_field.name) + '/$'
                ),
                csrf_exempt(relationship_view.as_view()),
                name='%s_%s_%s_relationship' % (
                    opts.app_label,
                    opts.model_name,
                    rel_slug
                )
            )
        )

        urlpatterns.append(
            url(
                (
                    '^' + slug + '/'
                    '(?P<' + (pk_field or 'pk') + '>[^/]+)'
                    '/' + urlise_field_name(rel_field.name) + '/$'
                ),
                csrf_exempt(relation_view.as_view()),
                name='%s_%s_%s' % (
                    opts.app_label,
                    opts.model_name,
                    rel_slug
                )
            )
        )

    return urlpatterns
