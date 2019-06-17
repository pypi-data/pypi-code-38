import json
import os
import rockset
import stat

VERSION_KEY = 'version'
VERSION_VALUE = 'v1'
AUTH_TOKEN_KEY = 'auth'
ACTIVE_PROFILE_KEY = 'active_profile'
PROFILES_KEY = 'profiles'

class Credentials(object):
    def __init__(self):
        # init config_dir to be `homedir`/.rockset
        self.config_dir = rockset.Client.config_dir()
        # init creds_file to be `config_dir`/.rockset/credentials
        self.creds_file = os.path.join(self.config_dir, 'credentials')

        # init creds
        self.creds = {
            VERSION_KEY: None,
            AUTH_TOKEN_KEY: None,
            ACTIVE_PROFILE_KEY: None,
            PROFILES_KEY: {},
        }
        self.read()
        return

    def setup(self):
        # Create config_dir if it doesn't exist
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        # bail if file already exists and has the correct version
        if self.creds[VERSION_KEY] == VERSION_VALUE:
            return

        # Create credentials_file or truncate it if exists
        # it either doesn't exist or is from previous version
        with os.fdopen(
                 os.open(self.creds_file, os.O_WRONLY | os.O_CREAT, 0o600),
                 'w') as _:
            os.chmod(self.creds_file, stat.S_IRUSR | stat.S_IWUSR)

        return

    def read(self):
        # init all available credentials
        if (os.path.exists(self.creds_file) and
            os.path.getsize(self.creds_file) > 0):
            with open(self.creds_file, 'r') as cfh:
                self.creds.update(json.load(cfh))
            self.migrate()
        return

    def migrate(self):
        modified = False
        # go through all api_server entries and rstrip('/')
        # implement all migration logic here when we bump VERSION_VALUE
        for profile in self.creds[PROFILES_KEY]:
            profile_details = self.creds[PROFILES_KEY].get(profile, {})
            api_server = profile_details.get('api_server', '')
            if api_server != api_server.rstrip('/'):
                profile_details.update({'api_server': api_server.rstrip('/')})
                modified = True
        if modified:
            self.save()
        return modified

    def save(self):
        with open(self.creds_file, 'w') as cfh:
            self.creds[VERSION_KEY] = VERSION_VALUE
            json.dump(self.creds, cfh, indent=4)
        return self.creds_file

    def active_profile(self, profile=None):
        if profile is not None and profile in self.creds[PROFILES_KEY]:
            self.creds[ACTIVE_PROFILE_KEY] = profile
        return self.creds[ACTIVE_PROFILE_KEY]

    def auth(self, user=None, auth_token=None):
        if auth_token is not None:
            if user is not None:
                auth_token.update({'user': user})
            self.creds[AUTH_TOKEN_KEY] = auth_token
        return self.creds[AUTH_TOKEN_KEY]

    def set(self, profile=None, api_key=None,
            api_server=None, auth_token=None):
        if profile is None:
            return None
        profile_details = self.creds[PROFILES_KEY].get(profile, {})
        if api_key is not None:
            profile_details.update({'api_key': api_key})
        if api_server is not None and len(api_server) > 0:
            if api_server[-1] == '/':
                api_server = api_server[:-1]
            profile_details.update({'api_server': api_server})
        if auth_token is not None:
            profile_details.update({'auth': auth_token})
        self.creds[PROFILES_KEY][profile] = profile_details
        return profile_details

    def get(self, profile=None):
        if profile is None:
            profile = self.active_profile()
        return self.creds[PROFILES_KEY].get(profile, {})

    def delete(self, profile):
        if self.creds[ACTIVE_PROFILE_KEY] == profile:
            self.creds[ACTIVE_PROFILE_KEY] = None
        return self.creds[PROFILES_KEY].pop(profile, None)

    def get_all_profiles(self):
        return self.creds[PROFILES_KEY]

