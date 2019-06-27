from ..api_autoregister import api

root = api.resource('/')


@root.get()
def root_view(ctx):
    return ctx.Response({'root': 'autoregistered'})
