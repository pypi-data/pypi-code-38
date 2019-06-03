"""Curate registry app user ajax
"""

import core_curate_app.permissions.rights as rights
import core_main_app.utils.decorators as decorators
from core_curate_app.views.user import ajax as curate_ajax


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def start_curate(request):
    """ Load forms to start curating.
    Add role to response url when POST.

    Args:
        request:

    Returns:

    """
    if request.method == 'GET':
        return curate_ajax.start_curate(request)
    elif request.method == 'POST':
        response = curate_ajax.start_curate(request)
        if response.status_code == 200:
            role = request.GET.get('role', None)
            response.content = "{0}?role={1}".format(response.content, role)
        return response
