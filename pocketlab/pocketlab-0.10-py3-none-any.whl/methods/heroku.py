__author__ = 'rcj1492'
__created__ = '2018.02'
__license__ = 'MIT'

def compile_instances(service_list):
    
    instance_list = []
    
# import dependencies
    from pocketlab.methods.validation import validate_platform
    from pocketlab import __module__
    from jsonmodel.loader import jsonLoader
    from jsonmodel.validators import jsonModel
    heroku_schema = jsonLoader(__module__, 'models/heroku-config.json')
    heroku_model = jsonModel(heroku_schema)

# construct account map
    account_map = {}
    for service in service_list:
        try:
        # retrieve services with heroku credentials
            heroku_details = validate_platform(heroku_model, service['path'], service['name'], '.lab')
            instance_details = {
                'id': '',
                'updated': '',
                'state': '',
                'login': heroku_details['heroku_account_email'],
                'machine': '',
                'image': '',
                'region': '',
                'access_key': heroku_details['heroku_auth_token'],
                'ip_address': heroku_details['heroku_app_subdomain'] + '.herokuapp.com',
                'name': heroku_details['heroku_app_subdomain'],
                'environment': 'prod',
                'services': service['name'],
                'tags': ''
            }
        # add service to account map
            if not heroku_details['heroku_account_email'] in account_map.keys():
                account_map[heroku_details['heroku_account_email']] = {
                    'token': heroku_details['heroku_auth_token'],
                    'apps': {}
                }
            app_name = heroku_details['heroku_app_subdomain']
            account_map[heroku_details['heroku_account_email']]['apps'][app_name] = instance_details
        except:
            pass

# construct instance list
    for key, value in account_map.items():

    # initialize heroku client
        from labpack.platforms.heroku import herokuClient
        heroku_kwargs = {
            'account_email': key,
            'auth_token': value['token'],
            'verbose': False
        }
        heroku_client = herokuClient(**heroku_kwargs)
        for app in heroku_client.apps:
            app_name = app['name']
            if app_name in value['apps'].keys():
                instance_details = value['apps'][app_name]
                instance_details['region'] = app['region']['name']
                instance_details['id'] = app['id']
                instance_details['updated'] = app['updated_at']
                instance_details['ip_address'] = app['web_url'].replace('https://','').replace('/','')
                instance_details['image'] = app['build_stack']['id']

            # find state of first non-idle dyno
                import json
                state_cmd = 'heroku ps -a %s --json' % app_name
                response = heroku_client._handle_command(state_cmd)
                dyno_list = json.loads(response)
                for dyno in dyno_list:
                    instance_details['state'] = dyno['state']
                    if dyno['state'] != 'idle':
                        break

            # find machine
                scale_cmd = 'heroku ps:scale -a %s' % app_name
                response = heroku_client._handle_command(scale_cmd)
                instance_details['machine'] = response.strip()

            # add details to list
                instance_list.append(instance_details)
    
    return instance_list