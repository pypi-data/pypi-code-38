from __future__ import print_function

import os
import re

import burlap
from burlap import ContainerSatchel
from burlap.constants import *
from burlap.decorators import task

fabfile_template = os.path.join(
    os.path.dirname(burlap.__file__),
    'templates',
    'burlap',
    'fabfile.py.template',
)

def md(d):
    if os.path.isdir(d):
        return
    os.makedirs(d)

def to_camelcase(value):
    value = re.sub(r'[^a-zA-Z0-9]+', ' ', value).strip()
    return ''.join(x.capitalize() for x in value.split(' '))

def init_dj(project_name, default_roles, virtualenv_dir='.env', version=None, **kwargs):

    site_name = project_name

    print('Installing Django...')
    if version:
        os.system('%s/bin/pip install Django==%s' % (virtualenv_dir, version))
    else:
        os.system('%s/bin/pip install Django' % virtualenv_dir)

    print('Initializing Django project...')
    if not os.path.isdir('src/%s' % site_name):
        print('Initializing base django project...')
        os.system('. %s/bin/activate; django-admin.py startproject %s src; deactivate' % (virtualenv_dir, site_name,))
        _settings_fn = os.path.abspath('src/%s/settings.py' % project_name)
        _content = open(_settings_fn, 'r').read()
        _sites = '''SITE_{name_upper} = "{name_lower}"
SITES = (
    SITE_{name_upper},
)
'''.format(
            name_upper=project_name.upper(),
            name_lower=project_name.lower(),
        )
        _top = []
        for _role in default_roles:
            _top.append("ROLE_%s = '%s'" % (_role.upper(), _role.lower()))
        _top.append('ROLES = (')
        for _role in default_roles:
            _top.append("    ROLE_%s," % (_role.upper(),))
        _top.append(')')
        _index = _content.find('"""\n\n')+4

        bottom_args = dict(
            app_name=project_name,
            app_name_title=project_name.title() + ' Administration',
            app_name_simple=project_name.title()
        )
        _bottom = '''
PROJECT_DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..'))

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    '%s/src/{app_name}/templates' % PROJECT_DIR,
)
# https://docs.djangoproject.com/en/1.11/ref/settings/#templates
TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {{
            #'loaders': TEMPLATE_LOADERS, # Unnecessary if we're using APP_DIRS.
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]
ADMIN_TITLE = '{app_name_title}'
ADMIN_TITLE_SIMPLE = '{app_name_simple}'
'''.format(**bottom_args)
        open(_settings_fn, 'w').write(_content[:_index]+_sites+('\n'.join(_top))+_content[_index:]+_bottom)

    print('Creating Django helper scripts...')
    open('src/manage', 'w').write('''#!/bin/bash
# Helper script for ensuring we use the Python binary in our local
# virtual environment when calling management commands.
# Otherwise, we'd have to always run `. ../.env/bin/activate`, which can be
# annoying.
# Be sue to run `fab <role> pip.init` first in order to setup
# the target role's Python virtual environment.
DIR=`dirname $0`;
cd $DIR;
../.env/bin/python manage.py $@''')
    open('src/runserver', 'w').write('''#!/bin/bash
# Helper script for running the local dev server, ensuring
# our virtual environment is used.
#set -e
#script_dir=`dirname $0`
#cd $script_dir
if [ -z "$PORT" ]; then
export PORT=8111
fi
if [ -z "$ROLE" ]; then
export ROLE=dev
fi
. ~/.bash_aliases
./manage runserver localhost:$PORT''')
    open('src/shell', 'w').write(r'''#!/bin/bash
# Creates a local PIP-aware shell.
#set -e
if [ $_ == $0 ]
then
echo "Please source this script. Do not execute."
exit 1
fi
#script_dir=`dirname $0`
#cd $script_dir
. .env/bin/activate
PS1="\u@\h:\W(fab)\$ "''')

    md('media')
    md('static')

    os.system('chmod +x src/shell')
    os.system('chmod +x src/manage')
    os.system('chmod +x src/runserver')

    # Create the primary app for containing models/urls/views.
    if not os.path.isdir('src/%s' % project_name):
        os.system('cd src; ./manage startapp %s' % (project_name,))

    os.system('cd src; ./manage syncdb')

class ProjectSatchel(ContainerSatchel):

    name = 'project'

    def set_defaults(self):
        pass

    def update_settings(self, d, role, path='roles/{role}/settings.yaml'):
        """
        Writes a key/value pair to a settings file.
        """
        try:
            import ruamel.yaml
            load_func = ruamel.yaml.round_trip_load
            dump_func = ruamel.yaml.round_trip_dump
        except ImportError:
            print('Warning: ruamel.yaml not available, reverting to yaml package, possible lost of formatting may occur.')
            import yaml
            load_func = yaml.load
            dump_func = yaml.dump
        settings_fn = path.format(role=role)
        data = load_func(open(settings_fn), Loader=yaml.SafeLoader)
        data.update(d)
        settings_str = dump_func(data)
        open(settings_fn, 'w').write(settings_str)

    @task
    def create_skeleton(self, project_name, roles='', components='', pip_requirements='', virtualenv_dir='.env', **kwargs):

        assert project_name, 'Specify project name.'
        site_name = project_name

        app_name = project_name

        default_roles = [_ for _ in roles.split(',') if _.strip()]
        default_components = [_.strip().lower() for _ in components.split(',') if _.strip()]

        print('Creating folders...')
        md('roles/all')
        for _role in default_roles:
            md('roles/%s' % _role)
        md('src')

        print('Creating roles...')
        open('roles/all/settings.yaml', 'w').write(
            self.render_to_string(
                'burlap/all_settings.yaml.template',
                extra=dict(project_name=project_name, site_name=site_name, app_name=app_name)))
        for _role in default_roles:
            open('roles/%s/settings.yaml' % _role, 'w').write(
                self.render_to_string(
                    'burlap/role_settings.yaml.template',
                    extra=dict(project_name=project_name, site_name=site_name, role=_role)))

        default_packages = pip_requirements.split(',')
        if default_packages:
            open('roles/all/pip-requirements.txt', 'w').write('\n'.join(default_packages))

        print('Adding global apt-requirements.txt...')
        open('roles/all/apt-requirements.txt', 'w').write('')

        print('Adding fabfile...')
        content = open(fabfile_template, 'r').read()
        content = content.format(project_name=project_name)
        open('fabfile.py', 'w').write(content.strip()+'\n')

        print('Initializing local development virtual environment...')
        os.system('virtualenv --no-site-packages %s' % virtualenv_dir)
        for package in default_packages:
            os.system('. %s/bin/activate; pip install %s; deactivate' % (virtualenv_dir, package))

        # Install burlap dependencies.
        burlap_pip_requirements = os.path.join(os.path.dirname(burlap.__file__), 'fixtures/requirements.txt')
        print('burlap_pip_requirements:', burlap_pip_requirements)
        assert os.path.exists(burlap_pip_requirements), 'Missing requirements file: %s' % burlap_pip_requirements
        for package in open(burlap_pip_requirements, 'r').readlines():
            if not package.strip():
                continue
            cmd = '%s/bin/pip install %s' % (virtualenv_dir, package)
            print('cmd:', cmd)
            assert not os.system(cmd)

        print('Adding bash setup...')
        open('setup.bash', 'w').write(self.render_to_string('burlap/setup.bash.template'))

        print('Adding gitignore...')
        open('.gitignore', 'w').write(self.render_to_string('burlap/gitignore.template'))

        args = kwargs.copy()
        args['project_name'] = project_name
        args['roles'] = roles
        args['default_roles'] = default_roles
        args['components'] = components
        args['pip_requirements'] = pip_requirements
        args['virtualenv_dir'] = virtualenv_dir
        for component in default_components:
            print('Setting up component %s...' % component)
            # Get component-specific settings.
            component_kwargs = dict(args)
            for _k, _v in kwargs.items():
                _key = component+'_'
                if _k.startswith(_key):
                    component_kwargs[_k[len(_key):]] = _v
                    del component_kwargs[_k]
            print('component_kwargs:', component_kwargs)
            try:
                globals()['init_%s' % component](**component_kwargs)
            except KeyError:
                pass

        print('='*80)
        print()
        print('Skeleton created for project %s!' % (project_name.title(),))
        print()

    @task
    def add_roles(self, roles):
        for role in roles:
            _role = role.strip().lower()
            fn = 'roles/%s/settings.yaml' % _role
            if os.path.isfile(fn):
                continue
            fn_dir = os.path.split(fn)[0]
            if not os.path.isdir(fn_dir):
                os.makedirs(fn_dir)
            open(fn, 'w').write(
                self.render_to_string('burlap/role_settings.yaml.template', extra=dict(role=_role)))
            print('Added role %s!' % role)

    @task
    def create_satchel(self, name):
        name_simple = re.sub(r'[^a-z0-9]+', '', name.lower())
        content = self.render_to_string(
            'burlap/satchel.py.template',
            extra=dict(
                name_camelcase=to_camelcase(name),
                name_simple=name_simple,
            ))
        if not os.path.isdir('satchels'):
            os.makedirs('satchels')
            os.system('touch satchels/__init__.py')
        satchel_fn = 'satchels/%s.py' % name_simple
        open(satchel_fn, 'w').write(content.strip()+'\n')
        print('Wrote %s.' % satchel_fn)

project = ProjectSatchel()
