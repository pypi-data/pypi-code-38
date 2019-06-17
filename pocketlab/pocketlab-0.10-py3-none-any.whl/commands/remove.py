__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

'''
remove services
'''

_remove_details = {
    'title': 'Remove',
    'description': 'Removes clutter from your records.',
    'help': 'removes a service from the registry',
    'benefit': 'Removes a service listing from the lab registry.'
}

from pocketlab.init import fields_model

def remove(service_name):

    title = 'remove'

# validate inputs
    input_fields = {
        'service_name': service_name
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

# construct registry client
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

# search for service name
    exit_msg = ''
    service_key = '%s.yaml' % service_name
    search_condition = [{ 0: { 'equal_to': service_key } }]
    search_filter = registry_client.conditional_filter(search_condition)
    search_results = registry_client.list(filter_function=search_filter)
    if not search_results:
        raise ValueError('"%s" does not exist in lab registry.' % service_name)
    else:
        registry_client.delete(search_results[0])
        exit_msg = '"%s" removed from lab registry.' % service_name

    return exit_msg
