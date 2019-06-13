from __future__ import division
import os
import fileutils
import shutil
from project import Project


def clone():
    out_folder = '{}/proj.ios'.format(fileutils.root_dir)
    if os.path.isdir(out_folder):
        shutil.rmtree(out_folder)
    cmd = 'git clone git@bitbucket.org:stereo7_tools/template_proj_ios_syn.git {}'.format(out_folder)
    print cmd
    os.system(cmd)
    shutil.rmtree('{}/.git'.format(out_folder))
    os.remove('{}/.gitignore'.format(out_folder))


def get_project_folder(arg_parser):
    folder = fileutils.root_dir + '/proj.ios/'
    return folder


def replace_values(kind, file):
    if not os.path.isfile(file):
        return
    content = open(file).read()
    content = content.replace('@{PACKAGE_NAME}', Project.instance.package)
    content = content.replace('@{APP_BUNDLE_NAME}', Project.instance.app_bundle_name)
    if kind and Project.instance.with_pro_version:
        content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['ios'][kind].facebook_id)
        content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['ios'][kind].flurry_id)
        content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['ios'][kind].appodeal_id)
    else:
        content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['ios'].facebook_id)
        content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['ios'].flurry_id)
        content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['ios'].appodeal_id)

    fileutils.write(file, content)


def copy_resources(arg_parser):
    proj_folder = get_project_folder(arg_parser)
    icons_lite = '{}/store/icons/'.format(fileutils.root_dir)
    icons_pro = '{}/store/icons/pro/'.format(fileutils.root_dir)
    if Project.instance.with_pro_version:
        icons_lite += 'lite/'
    icons = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024]
    for size in icons:
        icon_prefix = 'Icon-' if os.path.isfile('{}Icon-{}.png'.format(icons_lite, size)) else ''
        if Project.instance.with_pro_version:
            shutil.copy2('{}{}{}.png'.format(icons_lite, icon_prefix, size), '{}ios/Images.xcassets/AppIcon.lite.appiconset/{}.png'.format(proj_folder, size))
            shutil.copy2('{}{}{}.png'.format(icons_pro, icon_prefix, size), '{}ios/Images.xcassets/AppIcon.pro.appiconset/{}.png'.format(proj_folder, size))
        else:
            shutil.copy2('{}{}{}.png'.format(icons_lite, icon_prefix, size), '{}ios/Images.xcassets/AppIcon.appiconset/{}.png'.format(proj_folder, size))

    launch_dir = '{}/store/launch_images/'.format(fileutils.root_dir)
    files = ['640x960', '640x1136', '1024x768', '2048x1536', '2208x1242']
    for file in files:
        fullpath = launch_dir + file + '.png'
        shutil.copy2(fullpath, '{}ios/Images.xcassets/LaunchImage.launchimage/{}.png'.format(proj_folder, file))


def pod(arg_parser):
    proj_folder = get_project_folder(arg_parser)
    os.system('cd {};pod install'.format(proj_folder))


def run(arg_parser):
    clone()
    Project.instance.check_custom_package('ios')
    replace_values('', get_project_folder(arg_parser) + 'Syndicate.xcodeproj/project.pbxproj')
    replace_values('lite', get_project_folder(arg_parser) + 'ios/info.lite.plist')
    replace_values('pro', get_project_folder(arg_parser) + 'ios/info.pro.plist')
    replace_values('', get_project_folder(arg_parser) + 'ios/info.plist')
    copy_resources(arg_parser)
    pod(arg_parser)
