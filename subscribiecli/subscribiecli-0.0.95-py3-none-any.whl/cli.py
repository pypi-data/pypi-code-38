import click
import shutil
import os
from os import environ
import subprocess
import urllib.request
import re
import git
import inspect
import logging


@click.group()
def cli():
    pass


@cli.command()
@click.pass_context
def init(ctx):
    """ Initalise a new subscribie project """
    logging.info("Initalising a new subscribie project")
    # Get example .env file, rename & place it in current working directory
    logging.info("... getting example config.py file")
    response = urllib.request.urlopen('https://raw.githubusercontent.com/Subscribie/subscribie/master/subscribie/config.py.example')  # noqa
    configfile = response.read()
    fullpath = os.path.join('./instance/config.py')
    with open(fullpath, 'wb') as fh:
        fh.write(configfile)

    # Create instance folder for prod
        logging.info("creating instance folder for production use")
        try:
            shutil.rmtree('./venv/var/', ignore_errors=True)
        except Exception:
            pass
        try:
            os.makedirs('./venv/var/subscribie-instance/')
            logging.info("creating symlink to .env file")
            os.symlink(os.getcwd() + '/.env', os.getcwd() + '/venv/var/subscribie-instance/.env')
        except Exception:
            logging.warn("Warning: failed to create symlink to .env file for production use")
            pass

    # Get example jamla.yaml file, rename & place it in current working directory
    logging.info("getting example jamla.yaml file")
    response = urllib.request.urlopen('https://raw.githubusercontent.com/Subscribie/subscribie/master/subscribie/jamla.yaml.example')
    jamlafile = response.read()
    with open('jamla.yaml', 'wb') as fh:
        fh.write(jamlafile)
    # Replace static assets path
    static_folder = ''.join([os.getcwd(), '/themes/theme-jesmond/static/'])
    ctx.invoke(setconfig, static_folder=static_folder)
    try:
        os.mkdir('themes')
    except OSError:
        logging.warn("Failed to create themes directory")
    # Git clone default template
    try:
        logging.info("... cloning default template")
        git.Git('themes/').clone('https://github.com/Subscribie/theme-jesmond.git')
    except Exception as inst:
        logging.warn("Failed to clone default theme. Perhaps it's already cloned?")

    # Edit .env file with correct paths
    fp = open('.env', 'a+')
    fp.write(''.join(['JAMLA_PATH="', os.getcwd(), '/', 'jamla.yaml"', "\n"]))
    fp.write(''.join(['TEMPLATE_FOLDER="', os.getcwd(), '/themes/"', "\n"]))
    fp.close()
    ctx.invoke(initdb)
    logging.info("Done")


@cli.command()
def initdb():
    """ Initalise the database """
    if os.path.isfile('data.db'):
        logging.error('Error: data.db already exists.')
        return -1

    with open('data.db', 'w'):
        logging.info('... creating data.db')
        pass
    logging.info('... running initial database creation script')
    response = urllib.request.urlopen('https://raw.githubusercontent.com/Subscribie/subscribie/master/subscribie/createdb.py')
    createdb = response.read()
    exec(createdb) #TODO change all these to migrations


@cli.command()
@click.option('--DB_FULL_PATH', default='./data.db', help="Full path to data.db")
def migrate(db_full_path):
    """ Run latest migrations """
    logging.info("... running migrations")
    migrationsDir = os.path.join(os.getcwd(), 'subscribie', 'migrations')
    for root, dirs, files in os.walk(migrationsDir):
        files.sort()
        for name in files:
            migration = os.path.join(root, name)
            logging.info("... running migration: " + name)
            subprocess.call("python " + migration + ' -up -db ' + db_full_path, shell=True)


@cli.command()
@click.option('--JAMLA_PATH', default=None, help='full path to \
               jamla.yaml')
@click.option('--SECRET_KEY', default=None, help='Random key for flask \
               sessions')
@click.option('--TEMPLATE_FOLDER', default=None, help='Path to theme \
               folder')
@click.option('--STATIC_FOLDER', default=None, help='Path to static assets \
               folder')
@click.option('--UPLOADED_IMAGES_DEST', default=None, help='Path to image\
               upload folder')
@click.option('--DB_FULL_PATH', default=None, help='Path to database')
@click.option('--SUCCESS_REDIRECT_URL', \
                default=None, \
                help='Mandate complete redirect url')
@click.option('--THANKYOU_URL', default=None, \
              help='Thank you url (journey complete url)')
@click.option('--MAIL_SERVER', default="127.0.0.1", help='Mail server hostname or IP')
@click.option('--MAIL_PORT', default=25, type=int, help='Email submission port')
@click.option('--MAIL_DEFAULT_SENDER', default=None, help='Default mailserver from')
@click.option('--MAIL_USERNAME', default=None, help='Mailserver username')
@click.option('--MAIL_PASSWORD', default=None, help='Mailserver password')
@click.option('--MAIL_USE_TLS', default=True, help='Mailserver use TLS')
@click.option('--EMAIL_LOGIN_FROM', default=None, help='Default email from')
@click.option('--GOCARDLESS_CLIENT_ID', default=None, help='GoCardless client id \
              (not needed by default, unless doing a partner integration)')
@click.option('--GOCARDLESS_CLIENT_SECRET', default=None, help='GoCardless client \
               secret (not needed by default, unless doing partner integration')
@click.option('--TEMPLATE_BASE_DIR', default='./themes/', help="Set template base dir")
def setconfig(jamla_path, secret_key, template_folder, static_folder, \
              uploaded_images_dest, db_full_path, success_redirect_url, \
              thankyou_url, mail_server, mail_port, \
              mail_default_sender, mail_username, mail_password, mail_use_tls,\
              email_login_from, gocardless_client_id, \
              gocardless_client_secret, template_base_dir):
    """Updates the config.py which is stored in instance/config.py
    :param config: a dictionary
    """
    newConfig = ''
    with open('./instance/config.py', 'r') as fh:
        for line in fh:
            frame = inspect.currentframe()
            options = inspect.getargvalues(frame).args
            for option in options:
                if option.swapcase() in line and frame.f_locals[option] is not None :
                    newValue = ''.join([option.swapcase(), '="', str(frame.f_locals[option]), '"'])
                    expr = r"^" + option.swapcase() + ".*"
                    line = re.sub(expr, newValue, line)
                    logging.info("Writing: %s", newValue)
            newConfig = ''.join([newConfig, line])
    # Writeout new config file
    with open('./instance/config.py', 'w') as fh:
        fh.write(newConfig)

@cli.command()
@click.option('--name', help="Name of theme.", required=True, prompt="Theme name")
@click.option('--base', help="Base theme.", required=True, \
                prompt="Base theme name", default="jesmond")
def newtheme(name, base='jesmond'):
    """Create new theme"""
    logging.info("Creating new theme: " + name + " with base theme: " + base)
    #Create theme based on `base` theme
    newThemeDir = os.path.abspath(''.join([os.getcwd(), '/themes/theme-', name]))
    #Make theme path
    if os.path.isdir(newThemeDir) is False:
        try:
            os.makedirs(newThemeDir)
        except Exception as e:
            msg = ''.join(["Failed to create directory '", newThemeDir, \
                            "' for theme: '", name])
            logging.critical("Failed to create directory: {}, for theme: {}".format(newThemeDir, name))
    else:
        msg = ''.join(['Theme folder for "', name, '" already exists: ', \
                        newThemeDir])
        raise Exception(msg)

    # Copy from base theme
    try:
        repoUrl = ''.join(['https://github.com/Subscribie/theme-', base, '.git'])
        logging.info(''.join(['... cloning base theme: "', base , '" from ', \
                    repoUrl, ' into "', newThemeDir, '"']))
        git.Git(newThemeDir).clone(repoUrl, newThemeDir)
    except Exception as inst:
        msg = ''.join(['Error: Failed to clone base theme "', base, '" Perhaps \
                      its already cloned?'])
        logging.error(msg)

    # Rename base theme to name of new theme
    try:
        srcDir = os.path.abspath(''.join([newThemeDir, '/', base]))
        dstDir = os.path.abspath(''.join([newThemeDir, '/', name]))
        shutil.move(srcDir, dstDir)
    except:
        msg = ''.join(['Failed to move "', srcDir, '" to "', dstDir, '" ', \
                        'whilst renaming the base theme folder to "', base, '"'])
        raise Exception(msg)

    # Set config to point to new theme & static folders


@cli.command()
def run():
    """Run subscribie"""
    environ['FLASK_APP'] = 'subscribie'
    click.echo('Running subscribie...')
    subprocess.call("flask run", shell=True)


if __name__ == '__main__':
    cli()
