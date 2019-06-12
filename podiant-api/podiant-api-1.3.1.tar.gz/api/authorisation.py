from api.exceptions import (
    ConfigurationError,
    ForbiddenError,
    NotAuthenticatedError
)


class AuthBundle(object):
    """
    A simple object representing an authentication context (usually a string
    set either to 'list' or 'detail'), and information that would be useful to
    the authoriser (like the current object being requested).
    """

    def __init__(self, context='', **kwargs):
        """
        :param context: The current context (should be 'list' or 'detail').
        :type context: str

        Any data passed in via kwargs is available in the `data` property.
        """

        self.context = context
        self.data = kwargs


class AuthoriserBase(object):
    """
    Abstract class for authorisation.
    """

    def __init__(self, view):
        """
        Instantiate the authoriser by passing in the current view.

        :param view: The current view object
        :type view: ``django.views.base.View``
        """

        self.view = view

    def has_list_permission(self, request, bundle):  # pragma: no cover
        """
        Override this method to check whether a user has authorisation to
        view a list of objects.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        raise NotImplementedError('Methot not implemented')

    def has_detail_permission(self, request, bundle):  # pragma: no cover
        """
        Override this method to check whether a user has authorisation to
        view a specific object. The bundle may contain an `object` property
        which indicates the object the API client wants to view.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        raise NotImplementedError('Methot not implemented')

    def has_create_permission(self, request, bundle):  # pragma: no cover
        """
        Override this method to check whether a user has authorisation to
        create an object.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        raise NotImplementedError('Methot not implemented')

    def has_update_permission(self, request, bundle):  # pragma: no cover
        """
        Override this method to check whether a user has authorisation to
        update an existing object. The bundle may contain an `object` property
        which indicates the object the API client wants to update.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        raise NotImplementedError('Methot not implemented')

    def has_delete_permission(self, request, bundle):  # pragma: no cover
        """
        Override this method to check whether a user has authorisation to
        delete an object. The bundle may contain an `object` property
        which indicates the object the API client wants to delete.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        raise NotImplementedError('Methot not implemented')

    def authorise(self, request, bundle):
        """
        Given a request and an authentication bundle, this method will run
        the permission method that matches the current context and the HTTP
        operation being performed. If the method returns False, a
        :class:`~api.exceptions.ForbiddenError` exception is raised.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        perm, perm_name = None, None

        if bundle.context == 'list':
            if request.method in ('GET', 'HEAD'):
                perm = self.has_list_permission
                perm_name = 'list'
            elif request.method == 'POST':
                perm = self.has_create_permission
                perm_name = 'create'
        elif bundle.context == 'detail':
            if request.method in ('GET', 'HEAD'):
                perm = self.has_detail_permission
                perm_name = 'detail'
            elif request.method in ('PUT', 'PATCH'):
                perm = self.has_update_permission
                perm_name = 'update'
            elif request.method == 'DELETE':
                perm = self.has_delete_permission
                perm_name = 'delete'

        if perm is None:
            raise ForbiddenError(
                'Operation not permitted.',
                {
                    'permission': perm_name
                }
            )

        response = perm(request, bundle)
        if response is False:
            raise ForbiddenError(
                'Operation not permitted.',
                {
                    'permission': perm_name
                }
            )

        return response


class ReadOnlyAuthoriser(AuthoriserBase):
    """
    A simple authoriser that allows all read operations and denies all write
    operations.
    """

    def has_list_permission(self, request, bundle):
        """
        Allows objects to be listed.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """
        return True

    def has_detail_permission(self, request, bundle):
        """
        Allows object details to be viewed.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """
        return True

    def has_create_permission(self, request, bundle):
        """
        Denies objects from being created.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """
        return False

    def has_update_permission(self, request, bundle):
        """
        Denies objects from being updated.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """
        return False

    def has_delete_permission(self, request, bundle):
        """
        Denies objects from being deleted.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """
        return False


class DjangoUserAuthoriser(AuthoriserBase):
    """
    Authoriser based on the built-in Django user.
    """

    def is_anonymous(self, request):
        """
        Returns True if the user is not authenticated.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        """

        a = request.user.is_anonymous
        return a if not callable(a) else a()

    def has_model_perm(self, request, perm, obj=None):
        """
        Returns True if the requested model operation can be performed. If no
        model has been configured, a
        :class:`~api.exceptions.ConfigurationError` exception is raised. If the
        user is anonymous, a :class:`~api.exceptions.NotAuthenticatedError`
        exception is raised.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param obj: An optional model instance
        :type obj: ``django.db.models.Model``
        """

        if not hasattr(self.view, 'model'):  # pragma: no cover
            raise ConfigurationError('Model not defined')

        if self.is_anonymous(request):
            raise NotAuthenticatedError(
                'User not authenticated, or authentication details invalid.'
            )

        if perm == 'view':
            return True

        perm = '%s.%s_%s' % (
            self.view.model._meta.app_label,
            perm,
            self.view.model._meta.model_name
        )

        return request.user.has_perm(perm)

    def has_list_permission(self, request, bundle):
        """
        Returns True if the user has the 'view' permission for the given model.
        (The 'view' permission does not exist in Django, so the
        :func:`~DjangoUserAuthoriser.has_model_perm` method will always return
        True.)

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        return self.has_model_perm(request, 'view')

    def has_detail_permission(self, request, bundle):
        """
        Returns True if the user has the 'view' permission for the given model
        and/or object, passed in via the bundle. (The 'view' permission does
        not exist in Django, so the
        :func:`~DjangoUserAuthoriser.has_model_perm` method will always return
        True.)

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        return self.has_model_perm(
            request,
            'view',
            bundle.data.get('object')
        )

    def has_create_permission(self, request, bundle):
        """
        Returns True if the user has the 'create' permission for the given
        model.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        return self.has_model_perm(request, 'add')

    def has_update_permission(self, request, bundle):
        """
        Returns True if the user has the 'change' permission for the given
        model and/or object, passed in via the bundle.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        return self.has_model_perm(
            request,
            'change',
            bundle.data.get('object')
        )

    def has_delete_permission(self, request, bundle):
        """
        Returns True if the user has the 'delete' permission for the given
        model and/or object, passed in via the bundle.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        return self.has_model_perm(
            request,
            'delete',
            bundle.data.get('object')
        )


class GuestReadOnlyOrDjangoUserAuthoriser(DjangoUserAuthoriser):
    """
    Authoriser based on the
    :class:`~api.authorisation.DjangoUserAuthoriser`, but allowing read
    operations for anonymous users.
    """

    def has_list_permission(self, request, bundle):
        """
        Returns True if the user is anonymous, otherwise the 'view' permission
        for the model is checked.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        if self.is_anonymous(request):
            return True

        return super().has_list_permission(request, bundle)

    def has_detail_permission(self, request, bundle):
        """
        Returns True if the user is anonymous, otherwise the 'view' permission
        for the model and/or object (as passed in via the bundle) is checked.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        :param bundle: The authentication bundle
        :type bundle: :class:`api.authorisation.AuthBundle`
        """

        if self.is_anonymous(request):
            return True

        return super().has_detail_permission(request, bundle)

    def authorise(self, request, bundle):
        if bundle.context == 'list':
            return super().authorise(request, bundle)

        perm, perm_name = None, None
        if request.method in ('GET', 'HEAD'):
            perm = self.has_detail_permission
            perm_name = 'detail'
        elif request.method in ('PUT', 'PATCH'):
            perm = self.has_update_permission
            perm_name = 'update'
        elif request.method == 'DELETE':
            perm = self.has_delete_permission
            perm_name = 'delete'

        if perm is None:
            raise ForbiddenError(
                'Operation not permitted.',
                {
                    'permission': perm_name
                }
            )

        response = perm(request, bundle)
        if response is False:
            raise ForbiddenError(
                'Operation not permitted.',
                {
                    'permission': perm_name
                }
            )

        return response
