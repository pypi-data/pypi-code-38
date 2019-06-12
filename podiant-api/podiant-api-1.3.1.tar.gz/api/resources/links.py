from api import settings
from api.exceptions import ConfigurationError
from api.utils import get_id_field, get_object_id
from django.db.models import Model, QuerySet
from django.urls import reverse
from urllib.parse import parse_qs, urlencode


class ResourceLink(object):
    """
    Represents a link to a single resource, a list of resources, or a
    relationship between resources. The resulting object can be added to an
    API response, and is resolved at the point of serialisation, since
    resources aren't request-aware.

    To create a link to an object, instantiate the class with the instance of
    the Django model, like so::

        task = Task.objects.get(pk=1)
        link = ResourceLink(obj)

    To create a link to a list of objects, instantiate the class with a
    model queryset::

        tasks = Task.objects.all()
        link = ResourceLink(tasks)

    You can link to a specific page in a pginated set of objects like so::

        tasks = Task.objects.all()
        link = ResourceLink(tasks, page=3)

    You can create a link to a model relation (which returns the related object
    or objects as primary data), like so::

        task = Task.objects.get(pk=1)
        creator_link = ResourceLink(task, 'creator')

        task_list = List.objects.get(pk=1)
        tasks_link = ResourceLink(task_list, 'tasks')

    You can create a link to a model relationship (which returns the related
    object ID(s) as primary data), like so::

        task_list = List.objects.get(pk=1)
        link = ResourceLink(task_list, 'tasks', 'relationship')

    You can also create a link to a named URL pattern by passing in the name
    as the first argument, and an optional `kwargs` which lists the kwargs
    needed to reverse the URL::

        task_list = List.objects.get(pk=1)
        link = ResourceLink('api:todos_task_detail', kwargs={'id': 1})
    """

    def __init__(self, obj, field=None, kind=None, page=None, kwargs={}):
        from . import registry

        def n(u):
            if settings.URL_NAMESPACE:
                return '%s:%s' % (settings.URL_NAMESPACE, u)

            return u

        self.urlname = None
        self.kwargs = {}
        self.args = ()
        self.qs = {}
        self.is_pagination_link = False

        if isinstance(obj, QuerySet):
            self.urlname = n('%s_%s_list') % (
                obj.model._meta.app_label,
                obj.model._meta.model_name
            )

            if page:
                self.qs['page'] = page
                self.is_pagination_link = True

            return

        if isinstance(obj, Model):
            try:
                resource = registry.get(type(obj), 'detail')
            except KeyError:  # pragma: no cover
                raise ConfigurationError(
                    (
                        '%s.%s object cannot be linked to, as no API '
                        'resource exists'
                    ) % (
                        obj._meta.app_label,
                        obj._meta.model_name
                    )
                )

            if field is not None:
                field = obj._meta.get_field(field)
                self.urlname = n('%s_%s_%s') % (
                    obj._meta.app_label,
                    obj._meta.model_name,
                    field.name
                )

                if kind == 'relationship':
                    self.urlname += '_relationship'
                elif kind not in (None, 'relation'):  # pragma: no cover
                    raise ConfigurationError(
                        'Unknown link kind, \'%s\'' % kind
                    )

                id_value = getattr(obj, resource.pk_field)
                self.kwargs = {
                    resource.pk_field: id_value
                }

                return

            self.urlname = n('%s_%s_detail') % (
                obj._meta.app_label,
                obj._meta.model_name
            )

            id_field = get_id_field(obj)
            id_value = get_object_id(obj)

            self.kwargs = {
                id_field: id_value
            }

            return

        if isinstance(obj, str):
            self.urlname = obj
            self.kwargs = kwargs
            return

        raise ConfigurationError(  # pragma: no cover
            'Unable to determine how to create a link for given context'
        )

    def resolve(self, request):
        """
        Given a request, this resolves the current link object into an
        absolute URI string.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        """

        resolved = reverse(
            self.urlname,
            kwargs=self.kwargs
        )

        qs = parse_qs(request.META['QUERY_STRING'])

        if not self.is_pagination_link:
            if 'include' in qs:
                del qs['include']

        qs.update(self.qs)

        if any(qs):
            qs = '?%s' % urlencode(qs, doseq=True)
        else:
            qs = ''

        absolute = request.build_absolute_uri(
            '%s%s' % (resolved, qs)
        )

        return absolute
