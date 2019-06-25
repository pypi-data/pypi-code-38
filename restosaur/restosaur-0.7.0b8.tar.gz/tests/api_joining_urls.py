from restosaur.contrib.django import JsonAPI


api = JsonAPI('foo')
subapi = JsonAPI('bar')

baz = subapi.resource('/')


@baz.get()
def baz_view(ctx):
    return ctx.OK('baz here')


api.join(subapi)


urlpatterns = api.urlpatterns()
