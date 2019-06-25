import errno
import string
import textwrap
from pathlib import Path

import click
import yaml
from clickclick import Action

# EC2 instance memory in MiB
EC2_INSTANCE_MEMORY = {
    't2.nano': 500,
    't2.micro': 1000,
    't2.small': 2000,
    't2.medium': 4000,
    'm3.medium': 3750,
    'm4.large': 8000,
    'c4.large': 3750,
    'c4.xlarge': 7500
}


def copy_template(template_path: Path, path: Path, variables: dict):
    for d in template_path.iterdir():
        target_path = path / d.relative_to(template_path)
        if d.is_dir():
            copy_template(d, target_path, variables)
        elif target_path.exists():
            # better not overwrite any existing files!
            raise click.UsageError('Target file "{}" already exists. Aborting!'.format(target_path))
        else:
            with Action('Writing {}..'.format(target_path)):
                # pathlib,Path.parent.mkdir keyword argument "exist_ok" where implemented
                # in python 3.5 and backported only to python 2.7 pathlib2 - but not to python 3.4 pathlib
                try:
                    target_path.parent.mkdir(parents=True)
                except FileExistsError:
                    pass
                except IOError as e:
                    if e.errno != errno.EEXIST:
                        raise
                with d.open() as fd:
                    contents = fd.read()
                template = string.Template(contents)
                contents = template.safe_substitute(variables)
                with target_path.open('w') as fd:
                    fd.write(contents)


def prepare_variables(variables: dict):
    env = []
    for key, val in sorted(variables.get('env', {}).items()):
        env.append({'name': str(key), 'value': str(val)})
    # FIXME: the indent is hardcoded and depends on formatting of deployment.yaml :-(
    variables['env'] = textwrap.indent(yaml.dump(env, default_flow_style=False), ' ' * 12)
    return variables


def read_senza_variables(fd):
    variables = {}
    data = yaml.safe_load(fd)

    senza_info = data.get('SenzaInfo')
    if not senza_info:
        raise click.UsageError('Senza file has not property "SenzaInfo"')

    variables['application'] = senza_info.get('StackName')

    components = data.get('SenzaComponents')
    if not components:
        raise click.UsageError('Senza file has no property "SenzaComponents"')

    for component in components:
        for name, definition in component.items():
            type_ = definition.get('Type')
            if not type_:
                raise click.UsageError('Missing "Type" property in Senza component "{}"'.format(name))
            if type_ == 'Senza::TaupageAutoScalingGroup':
                taupage_config = definition.get('TaupageConfig')
                if not taupage_config:
                    raise click.UsageError('Missing "TaupageConfig" property in Senza component "{}"'.format(name))
                # just assume half the main memory of the EC2 instance type
                variables['memory'] = '{}Mi'.format(round(
                                      EC2_INSTANCE_MEMORY.get(taupage_config.get('InstanceType'), 1000) * 0.5))
                variables['image'] = taupage_config.get('source', '').replace('{{Arguments.ImageVersion}}',
                                                                              '{{{VERSION}}}')
                variables['env'] = taupage_config.get('environment', {})
                application_id = taupage_config.get('application_id')
                if application_id:
                    # overwrites default StackName
                    variables['application'] = application_id
            elif type_ in ('Senza::WeightedDnsElasticLoadBalancer', 'Senza::WeightedDnsElasticLoadBalancerV2'):
                variables['port'] = definition.get('HTTPPort')
                variables['health_check_path'] = definition.get('HealthCheckPath') or '/health'
                main_domain = definition.get('MainDomain')
                if main_domain:
                    variables['dnsname'] = main_domain

    if 'dnsname' not in variables:
        variables['dnsname'] = '{{{APPLICATION}}}.foo.example.org'
    return variables
