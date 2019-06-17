import os
import sys

from docopt import docopt
from rockset.credentials import Credentials
from .command import Command

def _format_secret(value):
    if value is None:
        return None
    i = 1
    if len(value) >= 20:
        i = 4
    return '%s**********%s' % (value[:i], value[-i:])

def _prompt_api_key(api_key=None):
    return  [ {
        'key': 'api_key',
        'message': 'Enter Rockset API key',
        'prompt': '  API Key',
        'default': {
            'display': _format_secret(api_key),
            'value': api_key,
        }
    } ]

def _prompt_api_server(api_server=None):
    return [ {
        'key': 'api_server',
        'message': 'Enter Rockset API server URL',
        'prompt': '  API Server',
        'default': {
            'display': api_server,
            'value': api_server,
        }
    } ]

def _interactive_prompt(config):
    out = {}
    for item in config:
        key = item['key']
        message = item['message']
        prompt = item['prompt']
        default = item['default']
        if 'display' in default:
            prompt += ' [%s]' % default['display']
        sys.stdout.write(message + '\n')
        sys.stdout.write(prompt + ': ')
        sys.stdout.flush()
        value = input()
        value = value.strip()
        if value == '':
            value = default.get('value', '')
        out[key] = value
    return out


class Configure(Command):
    def usage(self):
        return """
usage: rock configure [--help]
       rock configure [options]
       rock configure add <profile> [options]
       rock configure update <profile> [options]
       rock configure ls
       rock configure rm <profile>
       rock configure select <profile>

Manage Rockset credential profiles. Each profile is associated
with an API key and an API endpoint.

commands:
    add, update       create a new credentials profile or update an existing one
                      Default, when no profiles exist.
    ls                list all profiles.
                      Default, when 1 or more profiles exist.
    rm                remove profile
    select            select profile to use for subsequent rock commands

arguments:
    <profile>         name of the profile you wish to create or update

options:
  -h, --help                    show this help message and exit
  -k, --api_key=API_KEY         specify API key to use for subsequent commands
  -s, --api_server=API_SERVER   specify API server URL assigned to your account
        """

    def go(self):
        creds = Credentials()

        # determine default command when none is specified
        if (
            not self.add and not self.update and not self.ls and not self.rm and
            not self.select
        ):

            # this is the `rock configure [options]` case
            # each case is explicitly called out for code readability
            # if api_key or api_server is specified in command-line,
            # then do `rock configure add default`
            if self.api_key or self.api_server:
                self.add = True
                self.profile = 'default'
            # if this is just `rock configure` and no profiles are found
            # then do `rock configure add default`
            elif len(creds.get_all_profiles()) == 0:
                self.add = True
                self.profile = 'default'
            # else just list all profiles
            else:
                self.ls = True

        # update is same as add
        if self.add or self.update:
            new_profile = self.profile
            ip = creds.get(new_profile)
            ip['api_key'] = ip.get('api_key', None)
            ip['api_server'] = ip.get('api_server',
                'https://api.rs2.usw2.rockset.com')
            # dont prompt if command-line options are specified
            if self.api_key or self.api_server:
                ip['api_key'] = self.api_key or ip['api_key']
                ip['api_server'] = self.api_server or ip['api_server']
            else:
                ip = _interactive_prompt(
                    _prompt_api_key(ip['api_key']) +
                    _prompt_api_server(ip['api_server'])
                )
            ip['profile'] = new_profile
            profile_details = creds.set(
                profile=ip['profile'],
                api_key=ip['api_key'],
                api_server=ip['api_server']
            )
            if len(creds.get_all_profiles()) == 1:
                creds.active_profile(ip['profile'])
            creds.save()
        elif self.select:
            select_profile = self.profile
            active_profile = creds.active_profile(select_profile)
            if active_profile != select_profile:
                self.error('Could not switch to profile "%s"!' % select_profile)
            else:
                creds.save()
        elif self.rm:
            rm_profile = self.profile
            deleted_profile = creds.delete(rm_profile)
            if deleted_profile is None:
                self.error('No profile with name "%s" exists!' % rm_profile)
            else:
                creds.save()

        # print all profiles in alphabetical order
        all_profiles = creds.get_all_profiles()
        all_profile_names = list(all_profiles.keys())
        all_profile_names.sort()

        # accumulate formatted profiles
        profiles = []
        for pn in all_profile_names:
            profiles.append(
                self._format_profile(
                    pn, all_profiles[pn], creds.active_profile()
                )
            )

        self.print_list(
            0,
            profiles,
            field_order=['profile', 'api_server', 'api_key'],
            header=True
        )
        if self.format == 'text':
            self.lprint(0, 'Credentials stored in %s' % creds.creds_file)

        return 0

    def _format_profile(self, p, pd, ap):
        # prefix profile name with '*' if current
        if p == ap:
            prefix = '* '
        else:
            prefix = '  '
        pd['profile'] = prefix + p

        # don't show full api_key
        pd['api_key'] = _format_secret(pd.get('api_key', None))
        return pd
