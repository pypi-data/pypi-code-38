import subprocess
import shlex

GIT_INIT = """git init"""

GIT_GET_GLOBAL_USER = """git config --global --get user.name"""

GIT_GET_GLOBAL_EMAIL = """git config --global --get user.email"""

GIT_SET_LOCAL_USER = """git config user.name '{user}'"""

GIT_SET_LOCAL_EMAIL = """git config user.email '{email}'"""

GIT_ADD_REMOTE_ORIGIN = """git remote add origin git@{server}:{group}/{project}.git"""


def get_command_output(command):
    cmd = shlex.split(command)
    output = subprocess.run(cmd, encoding='ascii', check=True, stdout=subprocess.PIPE)
    return output.stdout.strip()


def call_command(command):
    cmd = shlex.split(command)
    subprocess.call(cmd)


def git_init():
    command = shlex.split(GIT_INIT)
    subprocess.call(command)


def git_get_global_user():
    return get_command_output(GIT_GET_GLOBAL_USER)


def git_get_global_email():
    return get_command_output(GIT_GET_GLOBAL_EMAIL)


def git_set_local_user(user):
    call_command(GIT_SET_LOCAL_USER.format(user=user))


def git_set_local_email(email):
    call_command(GIT_SET_LOCAL_EMAIL.format(email=email))


def git_add_remote_origin(server, group, project):
    call_command(GIT_ADD_REMOTE_ORIGIN.format(server=server,
                                              group=group,
                                              project=project))
