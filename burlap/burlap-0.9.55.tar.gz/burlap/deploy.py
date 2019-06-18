from __future__ import print_function

import sys
import socket
from pprint import pprint
from functools import partial

import yaml

import six

from fabric.api import execute, get

from burlap import ContainerSatchel
from burlap.constants import *
from burlap.decorators import task
from burlap.common import manifest_recorder, success_str, manifest_deployers_befores, topological_sort, resolve_deployer, \
    manifest_deployers_takes_diff, manifest_deployers, str_to_component_list, assert_valid_satchel, clean_service_name
from burlap import exceptions

def iter_dict_differences(a, b):
    """
    Returns a generator yielding all the keys that have values that differ between each dictionary.
    """
    common_keys = set(a).union(b)
    for k in common_keys:
        a_value = a.get(k)
        b_value = b.get(k)
        if a_value != b_value:
            yield k, (a_value, b_value)

def get_component_order(component_names):
    """
    Given a list of components, re-orders them according to inter-component dependencies so the most depended upon are first.
    """
    assert isinstance(component_names, (tuple, list))
    component_dependences = {}
    for _name in component_names:
        deps = set(manifest_deployers_befores.get(_name, []))
        deps = deps.intersection(component_names)
        component_dependences[_name] = deps
    component_order = list(topological_sort(component_dependences.items()))
    return component_order

def get_deploy_funcs(components, current_thumbprint, previous_thumbprint, preview=False):
    """
    Returns a generator yielding the named functions needed for a deployment.
    """
    for component in components:
        funcs = manifest_deployers.get(component, [])
        for func_name in funcs:

            #TODO:remove this after burlap.* naming prefix bug fixed
            if func_name.startswith('burlap.'):
                print('skipping %s' % func_name)
                continue

            takes_diff = manifest_deployers_takes_diff.get(func_name, False)

            func = resolve_deployer(func_name)
            current = current_thumbprint.get(component)
            last = previous_thumbprint.get(component)
            if takes_diff:
                yield func_name, partial(func, last=last, current=current)
            else:
                yield func_name, partial(func)

class DeploySatchel(ContainerSatchel):

    name = 'deploy'

    def set_defaults(self):
        self.env.lockfile_path = '~/burlap/deploy.lock'
        self.env.data_dir = '~/burlap'
        self._plan_funcs = None

    @task
    def init(self):
        """
        Initializes the configuration files on the remote server.
        """
        r = self.local_renderer
        #r.sudo('mkdir -p {data_dir}; chown {user}:{user} {data_dir}')
        r.run_or_local('mkdir -p {data_dir}')

    @task
    def purge(self):
        """
        The opposite of init(). Completely removes any manifest records from the remote host.
        """
        r = self.local_renderer
        r.run_or_local('[ -d {data_dir} ] && rm -Rf {data_dir} || true')

    @property
    def manifest_filename(self):
        """
        Returns the path to the manifest file.
        """
        r = self.local_renderer
        tp_fn = r.format(r.env.data_dir + '/manifest.yaml')
        return tp_fn

    def get_current_thumbprint(self, components=None):
        """
        Returns a dictionary representing the current configuration state.

        Thumbprint is of the form:

            {
                component_name1: {key: value},
                component_name2: {key: value},
                ...
            }

        """
        components = str_to_component_list(components)
        if self.verbose:
            print('deploy.get_current_thumbprint.components:', components)
        manifest_data = {} # {component:data}
        for component_name, func in sorted(manifest_recorder.items()):
            self.vprint('Checking thumbprint for component %s...' % component_name)
            manifest_key = assert_valid_satchel(component_name)
            service_name = clean_service_name(component_name)
            if service_name not in self.genv.services:
                self.vprint('Skipping unused component:', component_name)
                continue
            elif components and service_name not in components:
                self.vprint('Skipping non-matching component:', component_name)
                continue

            self.vprint('Retrieving manifest for %s...' % component_name)
            manifest_data[manifest_key] = func()
            if self.verbose:
                pprint(manifest_data[manifest_key], indent=4)

        return manifest_data

    def get_previous_thumbprint(self, components=None):
        """
        Returns a dictionary representing the previous configuration state.

        Thumbprint is of the form:

            {
                component_name1: {key: value},
                component_name2: {key: value},
                ...
            }

        """
        components = str_to_component_list(components)
        tp_fn = self.manifest_filename
        if self.file_exists(tp_fn):
            fd = six.BytesIO()
            get(tp_fn, fd)
            tp_text = fd.getvalue()
            manifest_data = {}
            raw_data = yaml.load(tp_text, Loader=yaml.Loader)  # SafeLoader can't load native tuples
            for k, v in raw_data.items():
                manifest_key = assert_valid_satchel(k)
                service_name = clean_service_name(k)
                if components and service_name not in components:
                    continue
                manifest_data[manifest_key] = v
            return manifest_data

    @task
    def lock(self):
        """
        Marks the remote server as currently being deployed to.
        """
        self.init()
        r = self.local_renderer
        if self.file_exists(r.env.lockfile_path):
            raise exceptions.AbortDeployment('Lock file %s exists. Perhaps another deployment is currently underway?' % r.env.lockfile_path)
        self.vprint('Locking %s.' % r.env.lockfile_path)
        r.env.hostname = socket.gethostname()
        r.run_or_local('echo "{hostname}" > {lockfile_path}')

    @task
    def unlock(self):
        """
        Unmarks the remote server as currently being deployed to.
        """
        self.init()
        r = self.local_renderer
        if self.file_exists(r.env.lockfile_path):
            self.vprint('Unlocking %s.' % r.env.lockfile_path)
            r.run_or_local('rm -f {lockfile_path}')

    @task
    def fake(self, components=None):#, set_satchels=None):
        """
        Update the thumbprint on the remote server but execute no satchel configurators.

        components = A comma-delimited list of satchel names to limit the fake deployment to.
        set_satchels = A semi-colon delimited list of key-value pairs to set in satchels before recording a fake deployment.
        """

        self.init()

        # In cases where we only want to fake deployment of a specific satchel, then simply copy the last thumbprint and overwrite with a subset
        # of the current thumbprint filtered by our target components.
        if components:
            current_tp = self.get_previous_thumbprint() or {}
            current_tp.update(self.get_current_thumbprint(components=components) or {})
        else:
            current_tp = self.get_current_thumbprint(components=components) or {}

        tp_text = yaml.dump(current_tp)
        r = self.local_renderer
        r.upload_content(content=tp_text, fn=self.manifest_filename)

        # Ensure all cached manifests are cleared, so they reflect the newly deployed changes.
        self.reset_all_satchels()

    def get_component_funcs(self, components=None):
        """
        Calculates the components functions that need to be executed for a deployment.
        """

        current_tp = self.get_current_thumbprint(components=components) or {}
        previous_tp = self.get_previous_thumbprint(components=components) or {}

        if self.verbose:
            print('Current thumbprint:')
            pprint(current_tp, indent=4)
            print('Previous thumbprint:')
            pprint(previous_tp, indent=4)

        differences = list(iter_dict_differences(current_tp, previous_tp))
        if self.verbose:
            print('Differences:')
            pprint(differences, indent=4)
        component_order = get_component_order([k for k, (_, _) in differences])
        if self.verbose:
            print('component_order:')
            pprint(component_order, indent=4)
        plan_funcs = list(get_deploy_funcs(component_order, current_tp, previous_tp))

        return component_order, plan_funcs

    @task
    def preview(self, components=None, ask=0):
        """
        Inspects differences between the last deployment and the current code state.
        """

        ask = int(ask)

        self.init()

        component_order, plan_funcs = self.get_component_funcs(components=components)

        print('\n%i changes found for host %s.\n' % (len(component_order), self.genv.host_string))
        if component_order and plan_funcs:
            if self.verbose:
                print('These components have changed:\n')
                for component in sorted(component_order):
                    print((' '*4)+component)
            print('Deployment plan for host %s:\n' % self.genv.host_string)
            for func_name, _ in plan_funcs:
                print(success_str((' '*4)+func_name))
        if component_order:
            print()

        if ask and self.genv.host_string == self.genv.hosts[-1]:
            if component_order:
                if not six.moves.input('Begin deployment? [yn] ').strip().lower().startswith('y'):
                    sys.exit(0)
            else:
                sys.exit(0)

    @task
    def push(self, components=None, yes=0):
        """
        Executes all satchel configurators to apply pending changes to the server.
        """
        from burlap import notifier
        service = self.get_satchel('service')
        self.lock()
        try:

            yes = int(yes)
            if not yes:
                # If we want to confirm the deployment with the user, and we're at the first server,
                # then run the preview.
                if self.genv.host_string == self.genv.hosts[0]:
                    execute(partial(self.preview, components=components, ask=1))

            notifier.notify_pre_deployment()
            component_order, plan_funcs = self.get_component_funcs(components=components)

            service.pre_deploy()
            for func_name, plan_func in plan_funcs:
                print('Executing %s...' % func_name)
                plan_func()
            self.fake(components=components)

            service.post_deploy()
            notifier.notify_post_deployment()

        finally:
            self.unlock()

deploy = DeploySatchel()
