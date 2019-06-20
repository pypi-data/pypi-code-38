import click
import os
import zipfile
from pipz.pipzlib import get_private_package_version, install_private_package, download_private_package, install_powershell_module, isAdmin, install_data
#import subprocess
import sys
import getpass
import pkg_resources
import re
import subprocess
from io import StringIO
import tempfile
import shutil


def common_libs():
    os.system('pip3 install ipywidgets')
    os.system('pip3 install cufflinks')
    os.system('pip3 install git+https://github.com/altair-viz/jupyter_vega')
    os.system('conda install -y bokeh')

def splitall(fn):
    parts = fn.split('/')
    real_parts = []
    for p in parts:
        real_parts += p.split('\\')
    return real_parts


def run(cmd, throw=True, dry=False):

    if dry:
        print(cmd)
        return 0, ''

    print('Running: ', cmd)
    text = ''
    try:
        with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p, StringIO() as buf:
            for line in p.stdout:
                print(line, end='')
                buf.write(line)
            text = buf.getvalue()
        returncode = 0
    except:
        returncode = 1

    print(returncode)
    if throw and returncode != 0:
        raise Exception('Error')
    return returncode, text

@click.group(invoke_without_command=True)
@click.option('--admin/--no-admin', default=False)
@click.option('--upgrade', default=False, is_flag=True)
@click.pass_context
def cli(ctx, admin, upgrade):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['admin'] = admin
    ctx.obj['upgrade'] = upgrade
    if admin and not isAdmin():
        raise Exception('Run the command with elevated priviledges.')

    nothing = True

    if upgrade:
        nothing = False
        status, output = run('pip3 install --upgrade --no-cache --no-cache-dir pipz')
        sys.exit(status)


@cli.command(name='install')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install(ctx, package, secret):
    if secret is None:
        secret = getpass.getpass()
    install_private_package(ctx, package, secret)

@cli.command(name='remote-version')
@click.option('--package', '-p', nargs=2, type=click.Tuple([str, str]), multiple=True)
@click.pass_context
def remote_version(ctx, package):
    result = {}
    for p in package:
        v = get_private_package_version(ctx, p[0], p[1])
        result[p[0]] = v
    print(result)

@cli.command(name='requires-update')
@click.option('--package', '-p', nargs=2, type=click.Tuple([str, str]), multiple=True)
@click.option('--verbose', is_flag=True)
@click.pass_context
def requires_update(ctx, package, verbose):
    requires_upgrade_list = []
    for p in package:
        try:
            local_version = pkg_resources.get_distribution(p[0]).version
            remote_version = get_private_package_version(ctx, p[0], p[1])
            if verbose:
                print(f'{p} local: {local_version}, remote: {remote_version}')
            if float(local_version) < float(remote_version):
                requires_upgrade_list.append(f'{p[0]} {local_version} -> {remote_version}')
        except:
            if verbose:
                print('Error determining status of package', p)

    if len(requires_upgrade_list) > 0:
        print('Status: Update is required')
    else:
        print('Status: OK')


@cli.command(name='install-module')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install_module(ctx, package, secret):
    if secret is None:
        secret = getpass.getpass()
    install_powershell_module(ctx, package, secret)

@cli.command(name='install-data')
@click.option('--package', default=None)
@click.option('--location', default='localdata')
@click.pass_context
def install_module(ctx, package, location):
    install_data(ctx, package, location)

@cli.command(name='install-requirements')
@click.argument('package')
@click.pass_context
def install_requirements(ctx, package):
    pipz_path = os.path.dirname(os.path.dirname(__import__('pipz').__file__))
    file = os.path.join(pipz_path, package, 'z-requirements.py')
    if not os.path.exists(file):
        return
    if os.path.exists(file):
        with open(file) as fp:
            for cnt, line in enumerate(fp):
                line = line[1:].strip()
                if line.startswith('run '):
                    ll = line[len('run '):]
                    os.system(ll)
                    continue

                if line.startswith('winrun ') and (sys.platform == "win32"):
                    ll = line[len('winrun '):]
                    os.system(ll)
                    continue

                if line.startswith('linrun ') and (sys.platform != "win32"):
                    ll = line[len('linrun '):]
                    os.system(ll)
                    continue


                if len(line) == 0 or line.startswith('#') or line.startswith(';'):
                    continue
                try:
                    package, secret = [x.strip() for x in line.split('--secret')]

                    if package.startswith('module:'):
                        # module = package[len('module:'):].strip()
                        # install_powershell_module(ctx, module, secret)
                        print('module skipped')
                    else:
                        install_private_package(ctx, package, secret)
                except Exception as e:
                    print("Error installing: {}".format(line))
                    print(e)
        return

    print('{} does not exist.'.format(file))


@cli.command(name='uninstall')
@click.argument('package')
@click.pass_context
def uninstall(ctx, package):
    os.system('pip3 uninstall {}'.format(package))


@cli.command(name='download')
@click.argument('package')
@click.option('--secret', default=None)
@click.option('--unzip', default=False)
@click.pass_context
def download(ctx, package, secret, unzip):
    if secret is None:
        secret = getpass.getpass()
    download_private_package(ctx, package, secret)
    if unzip:
        print('Unzip is not supported your. Please unzip the file manually')

@cli.command(name='ps')
@click.option('--str', default='')
@click.option('--process', default='')
@click.option('--down', default=False, is_flag=True)
@click.pass_context
def ps(ctx, str, process, down):
    cmd = 'powershell "Get-WmiObject -Class Win32_process'
    if process:
        cmd += '| ? {$_.Name -eq \'' + process + '\'}  '

    if str:
        cmd += '| ?{$_.CommandLine -like \'*' + str + '*\'} '

    cmd += '| ?{-not ($_.CommandLine  -like \'*get-wimobject*\')}| ?{-not ($_.CommandLine  -like \'*pipz  ps*\')}| ?{-not ($_.CommandLine  -like \'*pipz.exe*\')}|select processid, commandline'

    os.system(cmd)

    if down:
        os.system(cmd + '|foreach {stop-Process  -ID $_.ProcessId}')

@cli.command(name='docker-tree')
@click.option('--build', default=None)
@click.option('--repo', default=None)
@click.option('--tag', default=None)
@click.option('--dryrun', is_flag=True)
@click.option('--rebuild', is_flag=True)
@click.pass_context
def docker_tree(ctx, build, tag, dryrun, rebuild, repo):
    import glob
    from dockerfile_parse import DockerfileParser
    from pipz.node import node, get_node



    result = {}
    nodes = []
    original_dir = os.getcwd()
    cloned_repo = None
    completed_successfully = False
    is_absolute_path = False
    try:
        if repo:
            tmpdir = tempfile.mkdtemp()
            cloned_repo = tmpdir
            group, project, *folders = repo.split('/')
            clone_cmd = f'git clone git@gitlab.com:{group}/{project} {tmpdir}'
            print(clone_cmd)
            os.system(clone_cmd)
            target_dir = [tmpdir] + folders
            new_dir = os.path.join(*target_dir)
            print(new_dir)
            os.chdir(new_dir)
            print(os.getcwd())
            if tag is None:
                status, new_tag = run('git describe --tags --long --always')
                tag = new_tag.strip()
                print(tag)
            is_absolute_path = True

        wd = os.getcwd()
        wd_pars = wd.split(os.sep)

        for df in glob.iglob('**/Dockerfile', recursive=True):
            print(df)
            df_parts = df.split(os.sep)
            full_path = wd_pars + df_parts
            docker_image = f'jmulla/{full_path[-2]}'
            fn = os.path.join(*full_path)
            fn = fn.replace(':', f':{os.sep}')

            if os.name != 'nt' and is_absolute_path:
                fn = '/'+fn

            print(fn)
            d = DockerfileParser(fn)
            from_info, = [x for x in d.structure if x['instruction'] == 'FROM']
            from_val = from_info['value']
            if '/' not in docker_image:
                f'jmulla/{docker_image}'
            result[docker_image] = from_val

            parent_nodes = [x for x in nodes if x.value == from_val]
            if len(parent_nodes) == 0:
                parent_node = node(from_val)
                nodes.append(parent_node)
            else:
                parent_node, = parent_nodes

            image_nodes = [x for x in nodes if x.value == docker_image]
            if len(image_nodes) == 0:
                docker_image_node = node(docker_image)
                nodes.append(docker_image_node)
            else:
                docker_image_node, = image_nodes

            docker_image_node.dockerfile = df
            parent_node.append_child(docker_image_node)

        root_nodes = [x for x in nodes if x.parent is None]

        if build or rebuild:
            for r in root_nodes:
                print(r)

        if rebuild or build:
            print('-------------------')
            if os.name == 'nt':
                script_lines = []
            else:
                script_lines = ['#!/bin/bash']


            for r in root_nodes:
                if build:
                    n = get_node(r, build)
                    downstram_processing = '--no-cache'
                elif rebuild:
                    n = r
                    downstram_processing = ''
                else:
                    print('there is nothing to do')
                    continue

                if n is not None:
                    # print('Upstream:', [x.value for x in n.upstream_nodes()])
                    # print('Downstream:', [x.value for x in n.downstream_nodes()])
                    # print(r)
                    if tag is None:
                        raise Exception('Must specify tag')
                    for x in n.upstream_nodes():
                        if '/' in x.value:
                            user, image = x.value.split('/')
                            if user == 'jmulla':
                                # script_lines.append(f'docker build git@gitlab.com:autox/swarm.git#master:images/{image} -t {user}/{image}:{tag} -t {user}/{image}:latest')
                                # script_lines.append(f'pipz update-image-ifrequired {x.dockerfile} --tag {tag}')

                                retcode, txt = run(f'docker build git@gitlab.com:autox/swarm.git#master:images/{image} -t {user}/{image}:{tag} -t {user}/{image}:latest', dry=dryrun)
                                if retcode != 0:
                                    raise Exception(txt)
                                retcode, txt = run(f'pipz update-image-ifrequired {x.dockerfile} --tag {tag}', dry=dryrun)
                                if retcode != 0:
                                    raise Exception(txt)


                    for x in n.downstream_nodes():
                        if '/' in x.value:
                            user, image = x.value.split('/')
                            if user == 'jmulla':
                                retcode, txt = run(f'docker build {downstram_processing} git@gitlab.com:autox/swarm.git#master:images/{image} -t {user}/{image}:{tag} -t {user}/{image}:latest', dry=dryrun)
                                if retcode != 0:
                                    raise Exception(txt)
                                retcode, txt = run(f'pipz update-image-ifrequired {x.dockerfile} --tag {tag}', dry=dryrun)
                                if retcode != 0:
                                    raise Exception(txt)

        completed_successfully = True
    finally:
        os.chdir(original_dir)
        if cloned_repo and completed_successfully:
            shutil.rmtree(cloned_repo, ignore_errors=True)

@cli.command(name='update-image-ifrequired')
@click.argument('dockerfile')
@click.option('--tag', default=None)
@click.pass_context
def update_image(ctx, dockerfile, tag):
    from dockerfile_parse import DockerfileParser
    from pipz.node import node, get_node

    dockerfile_parts = splitall(dockerfile)
    if len(dockerfile_parts) <= 1:
        raise Exception('Cannot extract imagename from Dockerfile. Include parent folder in path')

    user = 'jmulla'
    image = dockerfile_parts[-2]

    f = DockerfileParser(dockerfile)
    lines = [x.strip() for x in f.content.split('\n')]
    pipz_lines = [x for x in lines if 'pipz' in x]

    if len(pipz_lines) > 0:
        has_pipz = False
        cmd = ['pipz requires-update']
        for pipz_line in pipz_lines:
            ps = re.findall('pipz', pipz_line)
            if len(ps) > 1:
                raise Exception('Only one pipz per line is currently supported')

            parts = pipz_line.split()
            if '--secret' in parts:
                package = parts[parts.index('install') + 1]
                secret = parts[parts.index('--secret') + 1]
                cmd.append(f'-p {package} {secret}')
                has_pipz = True

        if has_pipz:
            cmd = ' '.join(cmd)
            docker_cmd = f'docker run jmulla/{image} {cmd}'
            #print(docker_cmd)
            #output = subprocess.check_output(docker_cmd.split())
            status, output = run(docker_cmd)
            if 'Status: Update is required' in output: #.decode('utf-8'):
                print('Update is required')
                update_cmd = f'docker build --no-cache git@gitlab.com:autox/swarm.git#master:images/{image} -t {user}/{image}:{tag} -t {user}/{image}:latest'
                run(update_cmd)

@cli.command(name='run-test')
@click.pass_context
def run_test(ctx):
    run('dir')
    a,b = run('docker run jmulla/ds pipz requires-update -p selectstream globlib -p rmq globlib')


if __name__ == '__main__':
    cli(obj={'ok':1})
