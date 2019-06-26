

def find_context(request):
    """Find the context from the request

    http://stackoverflow.com/questions/10489544/getting-published-content-
    item-out-of-requestpublished-in-plone
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        context = request.PARENTS[0]
    return context


def get_nav_root(context):
    """Returns the navigation root"""

    plone_state = context.restrictedTraverse('@@plone_portal_state')
    return plone_state.navigation_root()
