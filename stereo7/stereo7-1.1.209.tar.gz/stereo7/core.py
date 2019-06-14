import version
import arguments
import inapps
import build
import os
import sys
from project import Project
import fileutils
import validate
import compress_images
import create_sublime_project
import generate_android_project
import generate_xcode_project
import locales
import hockeyapp
import firebase_testlab
from analytics.main import analytics


def console():
    main()


def _version():
    print version.__version__


def main():
    parser = arguments.Parser(sys.argv)
    command = parser.command

    fileutils.root_dir = os.path.abspath(parser.root)
    if not os.path.isdir(fileutils.root_dir):
        print 'Invalid path to project [{}]'.format(parser.root)
        exit(-1)

    if command == 'init':
        project = Project(parser, empty=True)
        project.create()
        exit(0)
    if command == 'version':
        print version.__version__
        exit(0)
    if command.startswith('an_'):
        analytics(command, parser)
        exit(0)

    Project.instance = Project(parser)

    if command == 'sublime':
        create_sublime_project.run()
    elif command == 'inapps_download':
        inapps.download_ios_metadata(Project.instance.apple_id)
    elif command == 'inapps':
        inapps.run(Project.instance.package,
                   Project.instance.name,
                   Project.instance.version,
                   Project.instance.gg_inapps,
                   parser)
    elif command == 'build':
        build.run(Project.instance.package,
                  Project.instance.version,
                  parser)
    elif command == 'robo-test':
        apk_path = parser.args['-binary_path']
        firebase_testlab.main(apk_path)
    elif command == 'gen-android':
        generate_android_project.run(parser)
    elif command == 'gen-ios':
        generate_xcode_project.run(parser)
    elif command == 'upload':
        build.upload(parser)
    elif command == 'upload_inapps':
        build.upload_inapps(parser)
    elif command == 'validate':
        validate.run()
    elif command == 'compress':
        compress_images.run(parser)
    elif command == 'locales':
        locales.download(Project.instance.gg_locales)
    elif command == 'create_locales_table':
        locales.convert_to_table()
    elif command == 'hockeyapp_upload':
        hockeyapp.hockey_app_upload(Project.instance, parser)
    else:
        print 'Unknown command [{}]'.format(command)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.extend('robo-test -binary_path /users/stereo7/Downloads/syndicate4-release.apk -r /work/td_core/projects/syndicate-4/'.split(' '))
    main()
