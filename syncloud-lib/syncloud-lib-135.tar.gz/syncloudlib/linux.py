from subprocess import check_output
import pwd


def useradd(user, home_folder=None):
    try:
        pwd.getpwnam(user)
        return 'user {0} exists'.format(user)
    except KeyError:
        options = '-r -s /bin/false'
        if home_folder:
            home_folder_options = '-m -d {0}'.format(home_folder)
            options = home_folder_options + ' ' + options
        command_line = '/usr/sbin/useradd {0} {1}'.format(options, user)
        return check_output(command_line, shell=True)
