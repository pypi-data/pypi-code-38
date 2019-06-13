import globus_sdk
import requests

CLIENT_ID = 'a9c9ecf0-f576-437a-8b35-98f966ac4475'

client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
client.oauth2_start_flow(requested_scopes="urn:globus:auth:scope:auth.globus.org:view_identities openid email profile urn:globus:auth:scope:nexus.api.globus.org:groups")

authorize_url = client.oauth2_get_authorize_url()
print('Please go to this URL and login: {0}'.format(authorize_url))

# this is to work on Python2 and Python3 -- you can just use raw_input() or
# input() for your specific version
get_input = getattr(__builtins__, 'raw_input', input)
auth_code = get_input(
    'Please enter the code you get after login here: ').strip()
token_response = client.oauth2_exchange_code_for_tokens(auth_code)

globus_auth_data = token_response.by_resource_server['auth.globus.org']
globus_nexus_data = token_response.by_resource_server['nexus.api.globus.org']
NEXUS_TOKEN = globus_nexus_data['access_token']
AUTH_TOKEN = globus_auth_data['access_token']

auth_authorizer = globus_sdk.AccessTokenAuthorizer(access_token=AUTH_TOKEN)
ac = globus_sdk.AuthClient(authorizer=auth_authorizer)

r = requests.get('https://www.globus.org/service/nexus/groups/143f5bdc-c127-11e4-ab32-22000a1dd033/members',
                         headers={"Authorization": "Bearer %s" % NEXUS_TOKEN})
print(r.json())

r = requests.get('https://nexus.api.globusonline.org/search?query=type%3Agroup%20pbcconsortium&include_identity_set_properties=true',
                         headers={"Authorization": "Bearer %s" % NEXUS_TOKEN})

print(r.json())