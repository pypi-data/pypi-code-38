import json
import os

from requests import Response

from ..client import *


#  oauth;
def signin_to_accounts_service(vc: VedavaapiSession, email, password):

    sign_in_post_data = {
        "email": email,
        "password": password
    }
    sign_in_post_response = vc.post('accounts/v1/oauth/signin', data=sign_in_post_data)
    print("signed in: \n", sign_in_post_response.json())


def create_oauth_client(
        signed_vc: VedavaapiSession, client_name, grant_types, client_type,
        redirect_uris=None, return_projection=None,
        marshal_to_google_structure=False, client_creds_persist_path=None):

    new_client_post_data = {
        "name": client_name,
        "grant_types": json.dumps(grant_types),
        "redirect_uris": json.dumps(redirect_uris) if redirect_uris else None,
        "client_type": client_type,
        "return_projection": return_projection,
        "marshal_to_google_structure": json.dumps(marshal_to_google_structure)
    }

    new_client_post_rep = signed_vc.post('accounts/v1/oauth/clients', data=new_client_post_data)
    print(new_client_post_rep.json())
    new_client_post_rep.raise_for_status()

    if client_creds_persist_path:
        open(client_creds_persist_path, 'wb').write(json.dumps(new_client_post_rep.json(), indent=2).encode('utf-8'))

    return new_client_post_rep.json()


def authorize_through_client_credentials_grant(
        vc: VedavaapiSession, client_id,
        client_secret, access_token_persist_path=None):
    request_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }

    resp = vc.post('accounts/v1/oauth/token', data=request_data)
    print(resp.json())
    resp.raise_for_status()
    if access_token_persist_path:
        open(access_token_persist_path, 'wb').write(json.dumps(resp.json(), indent=2).encode('utf-8'))
    return resp.json()


def authorize_throgh_client_creds_grant_from_file(
        vc: VedavaapiSession, client_creds_path, access_token_persist_path=None):
    client_json = json.loads(open(client_creds_path, 'rb').read().decode('utf-8'))
    if 'client_id' not in client_json or 'client_secret' not in client_json:
        return None

    return authorize_through_client_credentials_grant(
        vc, client_json['client_id'],
        client_json['client_secret'],
        access_token_persist_path=access_token_persist_path
    )


def create_test_implicit_client(
        vc: VedavaapiSession, client_name='test client',
        test_auth_server_port='6003', client_creds_persist_path=None):

    return create_oauth_client(
        vc, client_name, ['implicit'], 'public',
        redirect_uris=['http://localhost:{}/oauth_callback.html'.format(test_auth_server_port)],
        client_creds_persist_path=client_creds_persist_path)


def authorize_client_throgh_implicit_grant(
        vc, client_creds_path, access_token_persist_path, test_auth_server_port=6003):

    from vedavaapi.client.authorization_helper import Authorizer
    authorizer = Authorizer(
        vc.base_url, os.path.abspath(client_creds_path),
        os.path.abspath(access_token_persist_path),
        ['vedavaapi.root'], test_auth_server_port
    )
    authorizer.authorize()

# agents
## me_ns


def get_me(vc, projection=None):
    get_args = {
        "projection": projection
    }
    for k in list(get_args.keys()):
        if not get_args[k]:
            get_args.pop(k)

    user_resp = vc.get('accounts/v1/me', parms=get_args)
    user_resp.raise_for_status()
    return user_resp.json()

## users_ns

def find_user(vc, email):
    resp = vc.get("/accounts/v1/users", parms={
        "selector_doc" : json.dumps({'email' : email, "jsonClass": "User"})})
    print(resp.json())
    return resp.json()['items'][0] if is_success(resp) and resp.json()['items'] else None

def create_user(vc, new_user_email, new_user_pw, new_user_name, initial_team_id=None):
    new_user_json = {
        "jsonClass": "User",
        "email": new_user_email,
        "password": new_user_pw,
        "name": new_user_name
    }
    for k in list(new_user_json.keys()):
        if new_user_json[k] is None:
            new_user_json.pop(k)

    new_user_post_data = {
        "user_json": json.dumps(new_user_json)
    }
    if initial_team_id:
        new_user_post_data['initial_team_id'] = initial_team_id

    new_user_post_resp = vc.post('accounts/v1/users', data=new_user_post_data)  # type: Response
    if new_user_post_resp.status_code != 200:
        try:
            print(new_user_post_resp.json())
        except:
            pass

    new_user_post_resp.raise_for_status()
    return new_user_post_resp.json()


def get_user(vc: VedavaapiSession, user_id, projection=None):
    get_args = {
        "projection": projection
    }
    for k in list(get_args.keys()):
        if not get_args[k]:
            get_args.pop(k)

    user_resp = vc.get('accounts/v1/users/{}'.format(user_id), parms=get_args)
    user_resp.raise_for_status()
    return user_resp.json()


def delete_users(vc: VedavaapiSession, user_ids):

    delete_data = {
        "user_ids": json.dumps(user_ids)
    }
    response = vc.delete('accounts/v1/users', data=delete_data)
    response.raise_for_status()
    return response.json()

def delete_teams(vc: VedavaapiSession, team_ids):

    delete_data = {
        "team_ids": json.dumps(team_ids)
    }
    response = vc.delete('accounts/v1/teams', data=delete_data)
    response.raise_for_status()
    return response.json()


def get_resolved_user_teams(vc: VedavaapiSession, user_id, projection=None):
    get_args = {
        "teams_projection": projection
    }
    for k in list(get_args.keys()):
        if not get_args[k]:
            get_args.pop(k)

    resp = vc.get('accounts/v1/users/{}/teams'.format(user_id), parms=get_args)
    resp.raise_for_status()
    return resp.json()

# teams_ns


def create_team(vc: VedavaapiSession, team_name, team_description, parent_team_id):
    team_json = {
        "jsonClass": 'UsersTeam',
        "teamName": team_name,
        "description": team_description,
    }
    if parent_team_id:
        team_json["source"] = parent_team_id
    team_post_data = {
        "team_json": json.dumps(team_json),
        "return_projection": json.dumps({"permissions": 0})
    }

    team_post_response = vc.post('accounts/v1/teams', data=team_post_data)

    team_post_response.raise_for_status()
    return team_post_response.json()


def add_users_to_team(vc: VedavaapiSession, team_identifier, member_ids, team_id_type='_id'):
    post_data = {
        "identifier_type": team_id_type,
        "member_ids": json.dumps(member_ids)
    }

    resp = vc.post('accounts/v1/teams/{}/members'.format(team_identifier), data=post_data)
    resp.raise_for_status()

    return resp.json()
