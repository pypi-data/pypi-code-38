from api.exceptions import AlreadyRegisteredError


class ModelResourceRegistry(object):
    """
    A registry of model resources.
    """

    def __init__(self):
        self._details = {}
        self._lists = {}

    def register(self, model, list_class=None, detail_class=None, **kwargs):
        """
        Registers the resource for a model.

        :param model: The Django model to register
        :type model: ``django.db.models.Model``

        :param list_class: (optional) The resource list class to register
        :type list_class: :class:`ModelResource`

        :param detail_class: (optional) The resource detail class to register
        :type detail_class: :class:`ModelResourceList`

        The following keyword arguments can be supplied if ``list_class``
        and ``detail_class`` are ommitted:

        - ``order_by``:
            A list of fields to order objets by.
        - ``fields``:
            A list of local model fields to include in the resource.
        - ``exclude``:
            A list of local model fields to exclude from the resource.
        - ``relationships``:
            A list of related fields to include in the resource.
        - ``readonly_fields``:
            A list of fields that are not editable by the API user.
        - ``form_class``:
            A custom form class to be used to interact with model objects.
        - ``pk_field``:
            An alternative field to the standard primary key, used to identify
            the object.
        - ``paginate_by``:
            The number of records to return in a paginaged list.
        """

        if list_class is not None and detail_class is not None:
            return (
                self._register_list(model, list_class),
                self._register_detail(model, detail_class)
            )
        elif list_class is not None or detail_class is not None:
            raise TypeError(  # pragma: no cover
                'register takes 1 or 3 positional arguments'
            )
        else:
            from .models import ModelResource, ModelResourceList

            attrs = {
                'model': model
            }

            if 'order_by' in kwargs:
                attrs['order_by'] = kwargs['order_by']

            if 'fields' in kwargs:
                attrs['fields'] = kwargs['fields']

            if 'exclude' in kwargs:
                attrs['exclude'] = kwargs['exclude']

            if 'relationships' in kwargs:
                attrs['relationships'] = kwargs['relationships']

            if 'readonly_fields' in kwargs:
                attrs['readonly_fields'] = kwargs['readonly_fields']

            if 'form_class' in kwargs:
                attrs['form_class'] = kwargs['form_class']

            if 'pk_field' in kwargs:
                attrs['pk_field'] = kwargs['pk_field']

            detail_class = type(
                '%sResource' % model.__name__,
                (ModelResource,),
                attrs
            )

            if 'paginate_by' in kwargs:
                attrs['paginate_by'] = kwargs['paginate_by']

            list_class = type(
                '%sResourceList' % model.__name__,
                (ModelResourceList,),
                attrs
            )

            return self.register(model, list_class, detail_class)

    def _register_detail(self, model, kls):
        """
        Registers the detail resource.

        :param model: The model to register a resource for.
        :type model: ``django.db.models.Model``

        :param kls: The resource class.
        :type kls: :class:`ModelResource`
        """

        m = '%s.%s' % (
            model._meta.app_label,
            model._meta.model_name
        )

        if m in self._details:
            raise AlreadyRegisteredError(
                '%s is already registered.' % m
            )

        self._details[m] = kls
        return kls

    def _register_list(self, model, kls):
        """
        Registers the list resource.

        :param model: The model to register a resource for.
        :type model: ``django.db.models.Model``

        :param kls: The resource class.
        :type kls: :class:`ModelResourceList`
        """

        m = '%s.%s' % (
            model._meta.app_label,
            model._meta.model_name
        )

        if m in self._details:
            raise AlreadyRegisteredError(
                '%s is already registered.' % m
            )

        self._lists[m] = kls
        return kls

    def get(self, model, context):
        """
        Returns the correct model resource for the given context.

        :param model: The model to return the resource for.
        :type model: ``django.db.models.Model``

        :param context: The type of resource to return ('list' or 'detail')
        :type context: str
        """

        m = '%s.%s' % (
            model._meta.app_label,
            model._meta.model_name
        )

        if context == 'list':
            return self._lists[m]

        if context == 'detail':
            return self._details[m]
