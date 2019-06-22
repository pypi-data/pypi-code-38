from django.views.decorators.cache import never_cache


@never_cache
def with_id(request, coordinator, ctx, idx, action=None):
    api = coordinator(request, ctx, idx=idx, action=action)
    return api.run()


@never_cache
def without_id(request, coordinator, ctx, action=None):
    api = coordinator(request, ctx, action=action)
    return api.run()
