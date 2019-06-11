# encoding: utf-8

from apiutil.support.template_api.template_support_api_layer import TemplateAPILayer, EmptyTemplateAPILayer
from apiutil.support.apis.base_support_api import BaseSupportApi

# Create empty layer
empty_asl = EmptyTemplateAPILayer(host=u'jsonplaceholder.typicode.com',
                                  port=80,
                                  path_prefix=u'posts')

print(empty_asl.available_apis())
print(empty_asl.APIS)
print(empty_asl._api_mappings)


# Create the layer
asl = TemplateAPILayer(host=u'jsonplaceholder.typicode.com',
                       port=80,
                       path_prefix=u'posts')

print(empty_asl.available_apis())
print(empty_asl.APIS)
print(empty_asl._api_mappings)

print(asl.available_apis())
print(asl.APIS)
print(asl._api_mappings)

print(asl.available_api_versions(u'template'))
print(asl.template.example())

print(BaseSupportApi.merge_request_parameters(quote=False,
                                              parameters={u'x': 2,
                                                          u'y': u'y,y',
                                                          u'z': [1, u'z%z', u'z,z']},
                                              a=1,
                                              b=u'a b',
                                              c=[u'a a', u'b b', u'c c']))
