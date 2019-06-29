
##
#  gitlab.py
#  tagsnag
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 17.06.2019
#  Copyright (c) 2019 www.geeky.gent. All rights reserved.
#

import os.path
import gitlab
from pathlib import Path
from shutil import copyfile
import subprocess

class GitlabWrapper():
    """This class handles Gitlab related tasks"""

    ##
    # @REFACTOR: Apparently aenum's Enums cannot be pickled. I'm a bit
    # in a hurry to finish this project and the final presentation. Check
    # if there are other enum libraries...
    NEUTRAL_STATUS         = 0
    POSITIVE_STATUS        = 1
    NEGATIVE_STATUS        = 2
    ACTION_REQUIRED_STATUS = 3


    def __init__(self):
        self.initial_setup()


    def initial_setup(self):
        self.gitlab = None

        self.status_message = "Login required."
        self.status = GitlabWrapper.ACTION_REQUIRED_STATUS


    def login_with_token(self, url=None, token=None):
        if ((url == None) or (token == None)) or ((url == '') or (token == '')):
            self.status_message = 'Incomplete login information.'
            self.status = GitlabWrapper.ACTION_REQUIRED_STATUS
            return

        try:
            self.gitlab = gitlab.Gitlab(url,
                                        private_token = token)

            self.gitlab.auth()

            self.status_message = "Successfully logged into {}.".format(url)
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabAuthenticationError as e:
            self.status_message = 'Auth Error: {}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS


    def login_with_config(self):

        try:
            self.gitlab = gitlab.Gitlab.from_config('tagsnag',
                                                    [os.path.expanduser('/users/Tommi/.python-gitlab.cfg')])
            print(self.gitlab.auth())

            self.status_message = "Successfully logged into {}.".format(url)
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabAuthenticationError as e:
            self.status_message = 'Auth Error: {}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS


    def get_group_id(self, name):
        results = self.gitlab.groups.list(search = name)
        if len(results) > 0:
            # closest match
            return results[0].id

        return None


    def create_group(self, name, description='', visibility = 'internal'):
        group = None
        try:
            group = self.gitlab.groups.create({'name': name,
                                               'path': name,
                                               'description': description,
                                               'visibility': visibility}).id

            self.status_message = "Successfully created group."
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabCreateError as e:
            self.status_message = '{}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS

        finally:
            return group


    def create_project(self, name, description='', visibility = 'private', group_id = None):

        try:
            if group_id != None:
                return self.gitlab.projects.create({'name': name,
                                                    'description': description,
                                                    'visibility': visibility,
                                                    'namespace_id': group_id}).id
            else:
                return self.gitlab.projects.create({'name': name,
                                                    'description': description,
                                                    'visibility': visibility}).id


            self.status_message = "Successfully created project {}.".format(name)
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabCreateError as e:
            self.status_message = '{}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS


    def generate_projects(self, basename, count, description = '', group_name = None, administrators = []):

        p_id_url_map = {}

        if (group_name != None) and (group_name != ''):
            # Group exists and is not an empty string

            g_id = self.get_group_id(group_name)

            if (g_id == None):
                g_id = self.create_group(name = group_name,
                                         visibility = 'internal')


            # Assign administrators — Group
            if len(administrators) > 0:
                for user in administrators:
                    self.assign_admin_group(user = user,
                                            g_id = g_id)

            for idx in range(count, 0, -1):
                p_id = self.create_project(name = '{}_{}'.format(idx, basename),
                                           description = description,
                                           group_id = g_id,
                                           visibility = 'private')

                if p_id == None:
                    continue

                ssh_url = self.gitlab.projects.get(p_id).ssh_url_to_repo
                p_id_url_map[p_id] = ssh_url

        else:
            # No group

            for idx in range(count, 0, -1):
                p_id = self.create_project(name = '{}_{}'.format(idx, basename),
                                           description = description,
                                           visibility = 'private')

                if p_id == None:
                    continue

                ssh_url = self.gitlab.projects.get(p_id).ssh_url_to_repo
                p_id_url_map[p_id] = ssh_url

            # Assign administrators — Project
                if len(administrators) > 0:
                    for user in administrators:
                        self.assign_admin_repo(user = user,
                                               p_id = p_id)

        return p_id_url_map


    def assign_admin_group(self, user, g_id):

        try:
            group = self.gitlab.groups.get(g_id)
            users = self.gitlab.users.list(search=user)

            if len(users) > 0:
                # user = self.gitlab.users.get(1)
                user = users[0]
                member = group.members.create({'user_id': user.id,
                                               'access_level': gitlab.MAINTAINER_ACCESS})

            self.status_message = 'Assigned {} as maintainer for group.'.format(user)
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabCreateError as e:
            self.status_message = '{}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS


    def assign_admin_repo(self, user, p_id):

        try:
            project = self.gitlab.projects.get(p_id)
            users = self.gitlab.users.list(search=user)

            if len(users) > 0:
                # user = self.gitlab.users.get(1)
                user = users[0]
                member = project.members.create({'user_id': user.id,
                                                 'access_level': gitlab.MAINTAINER_ACCESS})

            self.status_message = 'Assigned {} as maintainer for project.'.format(user)
            self.status = GitlabWrapper.POSITIVE_STATUS

        except gitlab.exceptions.GitlabCreateError as e:
            self.status_message = '{}.'.format(e)
            self.status = GitlabWrapper.NEGATIVE_STATUS


    @staticmethod
    def get_default_config_path():
        cfg_name = '.python-gitlab.cfg'
        cfg_path = Path('{}/{}'.format(Path.home(), cfg_name))
        return cfg_path


    @staticmethod
    def config_exists():
        return Gitlab.get_default_config_path.exists()


    @staticmethod
    def copy_config():
        """ Copies config from package into home dir """

        if os.path.exists(path):
            try:
                copyfile(path, Gitlab.get_default_config_path)
            except IOError:
                print(IOError.message)
        else:
            print('File does not exist. Aborting...')

