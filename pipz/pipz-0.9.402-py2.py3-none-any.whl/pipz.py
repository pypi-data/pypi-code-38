import os
import click
import zipfile
import boto3
from tempfile import NamedTemporaryFile, mkdtemp


def unzip(key, directory):
    f = NamedTemporaryFile(delete=False)
    f.close()
    fn = f.name
    boto3.resource('s3').Bucket('whl').download_file(key, fn)

    file_name = os.path.abspath(fn)  # get full path of files
    zip_ref = zipfile.ZipFile(file_name)  # create zipfile object

    if not os.path.exists(directory):
        os.mkdir(directory)

    zip_ref.extractall(directory)  # extract file to dir
    zip_ref.close()  # close file
    os.unlink(file_name)  # delete zipped file

def install_powershell_module(module, secret):
    ps_dirs = os.environ['PSMODULEPATH'].split(';')
    existing_locations = []
    upgrade_locations = []
    for ps_dir in ps_dirs:
        if os.path.exists(ps_dir):
            ss_dir = os.path.join(ps_dir, module)
            existing_locations.append(ps_dir)
            if os.path.exists(ss_dir):
                upgrade_locations.append(ps_dir)

    upgrade_locations = list(set(upgrade_locations))
    if any(upgrade_locations):
        location, = upgrade_locations
    elif any(existing_locations):
        location = existing_locations[0]
    else:
        raise Exception("No existing PSMODULEPATH")

    module_location = os.path.join(location, module)

    if secret is None:
        unzip('{module}/{module}.zip'.format(module=module), module_location)
    else:
        unzip('{secret}/{module}/{module}.zip'.format(secret=secret, module=module), module_location)

@click.group()
@click.pass_context
def pipz(ctx):
    pass

@pipz.command()
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install(ctx, package, secret):
    if secret is None:
        os.system("pip install {lib} --no-cache-dir --upgrade --index-url http://s3.amazonaws.com/whl/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package))
    else:

        os.system("pip install {lib} --no-cache-dir --upgrade --index-url http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package, secret=secret))

@pipz.command(name='install-module')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install_module(ctx, package, secret):
    install_powershell_module(package, secret)



@pipz.command()
@click.argument('package')
@click.pass_context
def uninstall(ctx, package):
    os.system('pip uninstall {}'.format(package))

@pipz.command()
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def download(ctx, package, secret):
    if secret is None:
        os.system("pip download {lib} --no-cache-dir --no-deps --index-url http://s3.amazonaws.com/whl/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package))
    else:

        os.system("pip download {lib} --no-cache-dir --no-deps  --index-url http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{lib}/index.html --trusted-host s3.amazonaws.com".format(lib=package, secret=secret))



if __name__ == '__main__':
    pipz(obj={})
