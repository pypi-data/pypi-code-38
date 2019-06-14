from __future__ import division
import os
import fileutils
import shutil
from project import Project
import string


def istext(filename):
    s = open(filename).read(512)
    text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
    _null_trans = string.maketrans("", "")
    if not s:
        return True
    if "\0" in s:
        return False
    t = s.translate(_null_trans, text_characters)
    if float(len(t)) / float(len(s)) > 0.30:
        return False
    return True


def clone():
    out_folder = '{}/proj.android'.format(fileutils.root_dir)
    if os.path.isdir(out_folder):
        shutil.rmtree(out_folder)
    cmd = 'git clone git@bitbucket.org:stereo7_tools/template_proj_android_syn.git {}'.format(out_folder)
    os.system(cmd)
    shutil.rmtree('{}/.git'.format(out_folder))


def get_project_folder(arg_parser):
    folder = fileutils.root_dir + '/proj.android'
    if Project.instance.with_pro_version:
        folder = folder + '.' + arg_parser.app_kind
    folder += '/'
    return folder


def replace_values(arg_parser):
    folder = fileutils.root_dir + '/proj.android'
    if Project.instance.with_pro_version:
        out_folder = folder + '.' + arg_parser.app_kind
        if os.path.isdir(out_folder):
            shutil.rmtree(out_folder)
        os.rename(folder, out_folder)
        folder = out_folder
    folder += '/'

    project_name = Project.instance.project_name
    if Project.instance.with_pro_version:
        project_name += '.' + arg_parser.app_kind

    files = fileutils.getFilesList(folder)
    for file in files:
        file = folder + file
        if istext(file):
            content = open(file).read()
            package = Project.instance.package.replace('-', '')
            content = content.replace('@{PACKAGE_NAME}', package)
            content = content.replace('@{APP_BUNDLE_NAME}', Project.instance.app_bundle_name)
            content = content.replace('@{PROJECT_NAME}', project_name)
            if Project.instance.with_pro_version:
                kind = arg_parser.app_kind
                content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['android'][kind].facebook_id)
                content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['android'][kind].flurry_id)
                content = content.replace('@{GSM_APP_ID}', Project.instance.services['android'][kind].gsm_sender_id)
                content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['android'][kind].appodeal_id)
                content = content.replace('@{APP_KIND_DEFINE_FOLDER_ANDROID}', 'LOCAL_CPPFLAGS += -DRESOURCES_OVERRIDE_FOLDER=\\"%s\\"' % kind)
            else:
                content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['android'].facebook_id)
                content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['android'].flurry_id)
                content = content.replace('@{GSM_APP_ID}', Project.instance.services['android'].gsm_sender_id)
                content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['android'].appodeal_id)
                content = content.replace('@{APP_KIND_DEFINE_FOLDER_ANDROID}', '')

            fileutils.write(file, content)


def copy_resources(arg_parser):
    proj_folder = get_project_folder(arg_parser) + 'app/res/'
    icons = '{}/store/icons/'.format(fileutils.root_dir)
    if Project.instance.with_pro_version:
        icons += arg_parser.app_kind + '/'
    shutil.copy2('{}drawable-ldpi/icon.png'.format(icons), '{}drawable-ldpi/icon.png'.format(proj_folder))
    shutil.copy2('{}drawable-mdpi/icon.png'.format(icons), '{}drawable-mdpi/icon.png'.format(proj_folder))
    shutil.copy2('{}drawable-hdpi/icon.png'.format(icons), '{}drawable-hdpi/icon.png'.format(proj_folder))
    shutil.copy2('{}drawable-xhdpi/icon.png'.format(icons), '{}drawable-xhdpi/icon.png'.format(proj_folder))


def run(arg_parser):
    Project.instance.check_custom_package('android')
    clone()
    replace_values(arg_parser)
    copy_resources(arg_parser)
