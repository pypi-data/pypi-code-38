import os
import fileutils

android_task = '''curl \
    -F "status=2" \
    -F "notify=1" \
    -F "notes=None." \
    -F "notes_type=0" \
    -F "ipa=@{root}/../../Build/Android/{project}/outputs/apk/release/{project}-release.apk" \
    -H "X-HockeyAppToken: 520439d79df6430fb66b45937510cbad" \
    https://rink.hockeyapp.net/api/2/apps/{hockey_app_id}/app_versions/upload
'''

# ios_task = '''curl \
#     -F "status=2" \
#     -F "notify=1" \
#     -F "notes=None." \
#     -F "notes_type=0" \
#     -F "ipa=@ipa/{app}.ipa" \
#     -F "dsym=marines-mobile.app.dsym.zip" \
#     -H "X-HockeyAppToken: 520439d79df6430fb66b45937510cbad" \
#     https://rink.hockeyapp.net/api/2/apps/{hockey_app_id}/app_versions/upload
# '''


def hockey_app_upload(project, parser):
    if parser.platform == 'ios':
        print 'not supported hockey app upload for ios builds'
        exit(1)
    if not project.services[parser.platform].hockeyapp_id:
        exit(0)

    command = android_task
    command = command.replace('{root}', fileutils.root_dir)
    command = command.replace('{project}', project.project_name)
    command = command.replace('{hockey_app_id}', project.services[parser.platform].hockeyapp_id)
    print command

    result = False
    for i in xrange(5):
        result = 0 == os.system(command)
        if result:
            break

    if not result:
        print 'Cannot upload apk to hockey app'
        exit(2)
