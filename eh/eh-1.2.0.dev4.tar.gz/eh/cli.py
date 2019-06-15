# Copyright (c) 2016 Justin L. Hammond
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

import click 
import git
import inspect
import itertools
from stevedore import extension

from eh import base_subject as base
from eh import built_in_subject as bis


SUBJECT_EP = 'eh.subject_extensions'

command_settings = {
    'ignore_unknown_options': True,
}


class Eh(object):

    def __init__(self, debug, no_colors):
        self.subjects = {}
        self.subject_collections = []
        self.repo_subs = {}
        self.debug = debug
        self.no_colors = no_colors
        self._register_extensions('1.0')

        userhome = os.path.expanduser('~')
        self.eh_subject_repo = 'eh_subjects'
        self.eh_subject_dir = os.path.join(userhome, '.eh')
        self.eh_repo_dir = os.path.join(
            self.eh_subject_dir, self.eh_subject_repo)
        self.eh_subject_location = os.path.join(
            self.eh_repo_dir, 'subjects')
        self.git_subjects = 'https://github.com/roaet/eh_subjects'

        self._get_subjects_from_repo()

    def _load_subject_with_module(self, module, version):
        classes = inspect.getmembers(module, inspect.isclass)
        for cls_name, cls in classes:
            if hasattr(cls, 'versions'):
                if version not in cls.versions:
                    continue
            else:
                continue
            if issubclass(cls, base.BaseSubject):
                subject_ext = cls()
                self.subject_collections.append(subject_ext)
                for subject in subject_ext.subjects:
                    self.subjects[subject] = subject_ext

    def _discover_via_entrypoints(self):
        def fail2load(manager, entrypoint, exception):
            if self.debug:
                click.echo("Failed to load a subject: %s" % entrypoint)
                click.echo("Error is:\n%s" % exception)
            else:
                click.echo("A subject failed to load, please run with --debug")

        emgr = extension.ExtensionManager(
            SUBJECT_EP, invoke_on_load=False,
            on_load_failure_callback=fail2load)
        return ((ext.name, ext.plugin) for ext in emgr)

    def _register_extensions(self, version):
        for name, module in itertools.chain(self._discover_via_entrypoints()):
            self._load_subject_with_module(module, version)

    def _merge_subject_collections(self):
        final_subjects = {}
        final_parents = {}
        for collection in self.subject_collections:
            for subject in collection.subjects:
                final_subjects[subject] = collection.get_subject_unformatted(
                    subject)
            for parent in collection.parents:
                final_parents[parent] = {}
                for child in collection.get_children_for_parent(parent):
                    final_parents[parent][child] = (
                        collection.get_childsubject_unformatted(
                            parent, child))
        self.subjects = final_subjects
        self.parents = final_parents

    def find_and_output_subject(self, subject):
        if subject not in self.subjects:
            click.echo("I do not know anything about %s." % subject)
            exit(1)
        click.echo(base.BaseSubject.md_output(
            subject, self.subjects[subject], no_colors=self.no_colors))

    def run(self, subjects, **kwargs):
        self._merge_subject_collections()
        if len(subjects) == 1:
            self.find_and_output_subject(subjects[0])
        elif len(subjects) == 2:
            parent = subjects[0]
            subject = subjects[1]
            if parent not in self.parents:
                click.echo(
                    "I do not know anything about a parent subject called %s."
                    % parent)
                exit(1)
            if subject not in self.parents[parent]:
                click.echo(
                    "I do not know anything about %s with regards to %s" %
                    (subject, parent))
                exit(1)
            text = self.parents[parent][subject]
            click.echo(base.BaseSubject.md_output(
                subject, text, no_colors=self.no_colors))

    def _make_subject_list_from_repo(self):
        subs = bis.BuiltInSubjects(self.eh_subject_location)
        return subs

    def subject_list(self):
        click.echo("I know about: ")
        full_list = list(self.subjects.keys())
        full_list.extend(self.repo_subs.subjects)
        full_list.sort()
        for subject in full_list:
            click.echo('- %s' % subject)

    def _find_any_subjects(self):
        return [
            os.path.join(
                self.eh_subject_location, name) for name in os.listdir(
                    self.eh_subject_location) if os.path.isfile(
                        os.path.join(self.eh_subject_location, name))]

    def check_subjects_exists(self):
        if not os.path.exists(self.eh_subject_dir):
            if self.debug:
                click.echo("Could not find dir %s" % self.eh_subject_dir)
            return False
        if not os.path.exists(self.eh_repo_dir):
            if self.debug:
                click.echo("Could not find dir %s" % self.eh_repo_dir)
            return False
        if not os.path.exists(self.eh_subject_location):
            if self.debug:
                click.echo("Could not find dir %s" % self.eh_subject_location)
            return False
        if not self._find_any_subjects():
            if self.debug:
                click.echo("List of subjects are empty")
            return False
        return True

    def _setup_repo_directory(self):
        if not os.path.exists(self.eh_subject_dir):
            os.makedirs(self.eh_subject_dir)
        git.Repo.clone_from(self.git_subjects, self.eh_repo_dir)

    def _init_repo(self):
        try:
            self._setup_repo_directory()
        except git.exc.GitCommandError as e:
            click.echo("Failed to clone: %s" % e)
            exit(1)

    def _get_subjects_from_repo(self):
        if not self.check_subjects_exists():
            click.echo('Need to initialize subjects')
            self._init_repo()
        repo_subs = self._make_subject_list_from_repo()
        self.subject_collections.append(repo_subs)
        self.repo_subs = repo_subs

    def update_subject_repo(self):
        if not self.check_subjects_exists():
            click.echo('Need to initialize subjects')
            self._init_repo()
        else:
            g = git.cmd.Git(self.eh_repo_dir)
            g.pull()
            click.echo("Updated subjects")
            self._get_subjects_from_repo()
            self.subject_list()

@click.command(context_settings=command_settings)
@click.argument('subject', nargs=-1)
@click.option('--debug', is_flag=True)
@click.option('--no-colors', is_flag=True)
@click.pass_context
def main(context, subject, debug, no_colors):
    """
    Eh is a terminal program that will provide you with
    quick reminders about a subject.

    To get started run: eh help

    To figure out what eh knows about run: eh list

    To update the list of subjects: eh update

    Note:

    Eh will make a directory in your userhome called .eh
    where it will store downloaded subjects.
    """
    eho = Eh(debug, no_colors)
    if subject[0] == 'list':
        eho.subject_list()
        exit(0)
    if subject[0] == 'update':
        eho.update_subject_repo()
        exit(0)
    eho.run(subject)
    exit(0)
