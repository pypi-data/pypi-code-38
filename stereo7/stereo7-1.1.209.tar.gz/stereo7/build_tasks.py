import fileutils
from project import Project
import build_constants
import os
import xml.etree.ElementTree as ET


def os_system(cmd, message_on_error=''):
    print cmd
    result = os.system(cmd)
    if result != 0:
        if message_on_error:
            print message_on_error
        exit(-1)
    return True


def get_app_kind_suffix():
    if not Project.instance.with_pro_version:
        return ''
    else:
        return '.' + Project.instance.arg_parser.app_kind


def set_values(string, configuration='', scheme=''):
    string = string.replace('@{ROOT}', fileutils.root_dir)
    string = string.replace('@{APPLE_APP_ID}', Project.instance.apple_id)
    string = string.replace('@{APPLE_USER}', Project.instance.apple_auth_user)
    string = string.replace('@{APPLE_PASSWORD}', Project.instance.apple_auth_password)
    string = string.replace('@{APPLE_TEAM_ID}', Project.instance.apple_team_id)
    string = string.replace('@{CONFIGURATION}', configuration)
    string = string.replace('@{SCHEME}', scheme)
    string = string.replace('@{APP_KIND_SUFFIX}', get_app_kind_suffix())
    string = string.replace('@{XCODEPROJECT}', Project.instance.arg_parser.xcodeproj)
    return string


def windows_build(configuration):
    cmd = set_values(build_constants.win_cmd_build,
                     configuration=configuration
                     )
    os_system(cmd)


def android_change_version(packagename, app_version, build_version):
    path = fileutils.root_dir + '/proj.android{}/app/AndroidManifest.xml'.format(get_app_kind_suffix())
    ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
    try:
        handle = open(path, 'r')
        tree = ET.parse(handle)
        version = '{}.{}'.format(app_version, build_version) if build_version else app_version
        if build_version and str(build_version) != '0':
            tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionCode"] = str(build_version)
        tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionName"] = version
        tree.getroot().attrib["package"] = packagename
        tree.write(path, encoding='utf-8', xml_declaration=True)
    except:
        print 'cannot open file', path
        exit(-1)


def android_build(configuration):
    cmd = set_values(build_constants.android_cmd_build,
                     configuration=configuration
                     )
    os_system(cmd)


def android_upload_apk():
    cmd = set_values(build_constants.android_cmd_upload_apk)
    os_system(cmd)


def ios_change_version(packagename, app_version, build_version, app_kind):
    sh = '/usr/libexec/Plistbuddy'
    plist = 'Info.plist' if app_kind is None else 'info.%s.plist' % app_kind
    plist = '{}/proj.ios/ios/{}'.format(fileutils.root_dir, plist)
    version = '{}.{}'.format(app_version, build_version) if build_version else app_version
    os_system('{} -c "Set CFBundleShortVersionString {}" "{}"'.format(sh, version, plist))
    os_system('{} -c "Set CFBundleIdentifier {}" "{}"'.format(sh, packagename, plist))
    if build_version and str(build_version) != '0':
        os_system('{} -c "Set CFBundleVersion {}" "{}"'.format(sh, build_version, plist))


def ios_build_archive(scheme):
    build = set_values(build_constants.ios_cmd_build, scheme=scheme)
    os_system(build)


def ios_export_archive():
    export_create = set_values(build_constants.ios_export_plist)
    export = set_values(build_constants.ios_cmd_export)
    os_system(export_create)
    os_system(export)


def ios_upload_archive(scheme):
    upload = set_values(build_constants.ios_upload_shell, scheme=scheme)
    os_system(upload)


def ios_upload_inapps():
    upload_inapps = set_values(build_constants.ios_cmd_upload_inapps)
    os_system(upload_inapps)
