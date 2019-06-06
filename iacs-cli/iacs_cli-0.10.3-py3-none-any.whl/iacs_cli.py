import os, shutil, fileinput, sys, subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

import click

from .csv2md import csv2md


TEMPLATE = "https://github.com/richardskim111/iacs-course-template.git"


@click.command()
@click.argument('course_name', type=str)
def create(course_name):
    subprocess.call(['git', 'clone', '--quiet', TEMPLATE, course_name])

    course_dir = os.path.abspath(course_name)
    git_dir = os.path.join(course_dir, ".git/")
    shutil.rmtree(git_dir)

    # Create Root Directory
    readings_md = os.path.join(course_dir, 'README.md')
    with open(readings_md, "w") as file:
        file.write("# " + course_name + " Repository\n")

    # Write Pelican configuration file
    config_file = os.path.join(course_dir, 'config.py')
    with fileinput.input(files=config_file, inplace=True) as file:
        for i, line in enumerate(file):
            if 'COURSE_NAME =' in line:
                sys.stdout.write('COURSE_NAME = ' + '\'' +course_name + '\'\n')
            else:
                sys.stdout.write(line)


@click.command()
@click.option('--watch', '-w', is_flag=True)
@click.option('--file', '-f', type=str)
def publish(watch, file):
    root_dir = os.getcwd()
    if not os.path.exists(os.path.join(root_dir, 'config.py')):
        raise Exception("'publish' command must be executed in project root directory.")

    # Convert schedule.csv into a markdown file
    schedule_csv = os.path.join(root_dir, 'content/pages/schedule.csv')
    if os.path.isfile(schedule_csv):
        csv2md(schedule_csv)

    args = ['pelican', 'content', '-s', 'config.py', '-t', 'themes']
    if watch:
        args.append('-r')
    if file:
        args += ['--write-selected', file]
    subprocess.call(args)


@click.command()
@click.option('--port', '-p', default='8000')
def launch(port):

    root_dir = os.getcwd()
    if not os.path.exists(os.path.join(root_dir, 'config.py')):
        raise Exception("'launch' command must be executed in project root directory.")

    os.chdir('docs')
    port = int(port)

    with HTTPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        click.echo("Serving at localhost:{}, to quit press <ctrl-c>".format(port))
        httpd.serve_forever()



@click.command('copy', short_help="copy existing course project")
@click.argument('original', type=click.Path(exists=True), metavar='<original>', nargs=1)
@click.argument('course_name', type=click.Path(), metavar='<course_name>', nargs=1)
def copy(original, course_name):
    course_dir = os.path.abspath('./' + course_name)
    if not os.path.exists(course_dir):
        shutil.copytree(original, course_dir)

    # Remove existing git
    git = os.path.join(course_dir, '.git')
    if os.path.exists(git):
        shutil.rmtree(git)

    # Open config.py and change - COURSE_NAME, AUTHOR, SITEURL, GITHUB, NAVBAR_LINKS
    config_file = os.path.join(course_dir, 'config.py')
    with fileinput.input(files=config_file, inplace=True) as file:
        for i, line in enumerate(file):
            if 'COURSE_NAME =' in line:
                sys.stdout.write('COURSE_NAME = ' + '\'' +course_name + '\'\n')
            elif 'AUTHOR =' in line:
                sys.stdout.write('AUTHOR = \'\'\n')
            elif 'SITEURL =' in line:
                sys.stdout.write('SITEURL = \'\'\n')
            elif 'GITHUB =' in line:
                sys.stdout.write('GITHUB = \'\'\n')
            elif 'MENUITEMS =' in line:
                sys.stdout.write('MENUITEMS = []')
            else:
                sys.stdout.write(line)


@click.group()
def main():
    pass


main.add_command(create)
main.add_command(publish)
main.add_command(launch)
main.add_command(copy)


if __name__ == '__main__':
    main()
