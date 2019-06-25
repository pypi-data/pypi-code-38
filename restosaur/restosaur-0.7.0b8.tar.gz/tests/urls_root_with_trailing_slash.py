from restosaur.contrib.django import API

api = API('/api')
root = api.resource('/')


@root.get()
def root_view(ctx):
    return ctx.Response({'root': 'ok'})


urlpatterns = api.urlpatterns()
