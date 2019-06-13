# coding=utf-8
import six
from six.moves import configparser
import os
import click
import git
import gitlab
from enum import Enum

if six.PY2:
    import unicodecsv as csv
else:
    import csv


KEY_STUDENT_ID = 'student/id'
KEY_STUDENT_NAME_FIRST = 'student/name/first'
KEY_STUDENT_NAME_LAST = 'student/name/last'
KEY_INVALID = 'invalid'
KEY_STUDENT_GENDER = 'student/gender'


def relative_path(basedir, filename):
    """Creates a path relative to base"""
    return os.path.join(basedir, filename)


def create_gitlab(config):
    """Opens a gitlab instance with the supplied config.

    The environment variable EP2_GITLAB_KEY is the preferred source for the access token.
    If the variable is not provided, Gitlab.AccessToken from the configuration file is used"""
    access_token = os.environ.get("EP2_GITLAB_KEY")
    if access_token is None:
        access_token = config.get("Gitlab", "AccessToken")

    return gitlab.Gitlab(config.get("Gitlab", "URL"), private_token=access_token)


def create_config():
    """Loads the configuration file.

    Attempts to load the file from the EP2_CONF_FILE environment variable.
    If this variable is not present, it checks if the EP2_PATH environment variable is set.
    If it is set, $EP2_PATH/.ep2_gitlab is used as configuration file. If not, ~/.ep2_gitlab is used for config.
    """
    # Check for base path in env vars
    base = os.environ.get("EP2_PATH")
    if base is None:
        base = os.path.expanduser("~")

    # Load config file
    conf_file = os.environ.get("EP2_CONF_FILE")
    if conf_file is None:
        conf_file = relative_path(base, ".ep2_gitlab")

    config = configparser.SafeConfigParser()
    config.read(conf_file)
    return config


def tag_project(gl, project, tag, verbose):
    """Tags the last commit of a given project with 'tag'."""
    try:  # search for project
        project = gl.projects.get(project)
    except gitlab.exceptions.GitlabGetError:  # project not found
        click.secho('No repository exists for project ' + project, fg='red')
        return False

    if verbose:
        print('[DEBUG] Found project ' + project.web_url)

    master = project.branches.get('master')  # get master branch
    if verbose:
        print('[DEBUG] Found master branch with commit ' + master.commit['short_id'])

    commit_id = master.commit['id']  # get the id of the commit

    # TODO check timing constraints? e.g. commit time can't be later than 5 minutes after hand-in?
    try:
        project.tags.create({'tag_name': tag, 'ref': commit_id})  # create tag for commit
    except gitlab.exceptions.GitlabCreateError:  # tag already exists, fail gracefully
        click.secho('Tag already exists in project', fg='red')
        return False

    if verbose:
        print('[DEBUG] Added tag successfully')

    return True


def clone_or_update(gl, repo_dir, project, verbose, tag):
    """Clones or updates a repository into repo_dir"""

    try:
        project = gl.projects.get(project)  # find project on gitlab
    except gitlab.exceptions.GitlabGetError:
        click.secho('No repository exists for project ' + project, fg='red')  # no project has been found
        return False

    try:
        _ = project.tags.get(tag)  # look for tag in project, no need to check out untagged projects
    except gitlab.exceptions.GitlabGetError:
        if verbose:
            click.secho('No tag ' + tag + ' found in project ' + project.name_with_namespace.replace(' ', '')
                        + '. Trying for branch', fg='yellow')  # no tag has been found
        try:
            _ = project.branches.get(tag)
        except gitlab.exceptions.GitlabGetError:
            if verbose:
                click.secho('No branch ' + tag + ' found! Aborting clone/pull', fg='red')
            return False

    if os.path.exists(repo_dir):  # dir exists, no need to clone
        repo = git.Repo(repo_dir)
        origin = repo.remote("origin")
        if verbose:
            print('[DEBUG] dir exists, attempting pull')
        origin.fetch()  # fetch is enough, as checkout is performed later
    else:  # clone
        if verbose:
            print('[DEBUG] attempting clone')

        try:
            os.makedirs(repo_dir)
        except OSError:  # directory already exists
            pass

        if verbose:
            click.echo('[DEBUG] Cloning ' + project.ssh_url_to_repo + u' into ' + repo_dir)
        git.Git(repo_dir[:repo_dir.rindex(os.sep)]).clone(project.ssh_url_to_repo)  # clone repo

    try:
        git.Git(repo_dir).checkout(tag)  # checkout exercise tag
    except git.exc.GitCommandError:
        return False
    return True


def ue_repo(config, mat_no):
    """creates the path for a uebungs repository"""
    return os.path.join(config.get("Gitlab", "RepoPrefix"), 'uebung', mat_no).replace("\\", "/")


def submission_csv(config, group, ue):
    """Creates the path to the adhoc submission CSV file for an exercise for a group"""
    return os.path.join(tutor_repo(config), group, "adhoc_" + str(ue) + ".csv")


def attendance_csv(config, group, ue):
    """Creates the path to the attendance CSV file for an exercise for a group"""
    return os.path.join(tutor_repo(config), group, "attendance_" + str(ue) + ".csv")


def test_attendance_csv(config, test, slot):
    """Creates the path to the attendance CSV file for an exercise for a group"""
    return os.path.join(tutor_repo(config), 'tests', test, slot + ".csv")


def pre_eval_csv(config, group, ue):
    return os.path.join(tutor_repo(config), group, "pre_eval_%s.csv" % ue)


def students_csv(config, group):
    """Creates the path to the attendance CSV file for an exercise for a group"""
    return os.path.join(tutor_repo(config), group, "students.csv")


def test_students_csv(config, test):
    """Creates the path to the attendance CSV file for an exercise for a group"""
    return os.path.join(tutor_repo(config), 'tests', test, "students.csv")


def local_repo(config, mat_no):
    """Returns the local path of students uebungs repo"""
    return os.path.join(config.get('Local', 'GitHome'), 'uebung', mat_no)


def tutor_repo(config):
    """Returns the path to the local tutor directory"""
    return os.path.join(config.get('Local', 'GitHome'), 'org', 'tutorinnen')


def tutor_gender(config):
    """Returns the gender of a tutor"""
    try:
        return config.get('Personal', 'Gender')
    except configparser.NoSectionError:
        return 'female'


def template_path(config, group, template):
    """Returns the path of the template file to be used"""
    # if group is not None:
    #     template_file = os.path.join(tutor_repo(config), group, 'templates', template)
    #     if os.path.exists(template_file):
    #         return template_file
    template_file = os.path.join(tutor_repo(config), 'templates', template)
    if os.path.exists(template_file):
        return template_file
    return None


def string_normalize(str):
    if six.PY2:
        return str  # .decode('utf-8')
    else:
        return str


def students_csv_fieldnames():
    return [KEY_STUDENT_ID, KEY_STUDENT_NAME_LAST, KEY_STUDENT_NAME_FIRST, KEY_STUDENT_GENDER]


def test_students_csv_fieldnames():
    return [KEY_STUDENT_ID, KEY_STUDENT_NAME_LAST, KEY_STUDENT_NAME_FIRST]


def escape_csv_string(string):
    s = string_normalize(string)
    s = s.replace(';', u';')
    return s


def validate_headers(headers):
    return all({k == headers[k]: headers[k] for k in headers if not k == 'invalid'})


def check_row(row):
    return not any({row[k] is None: row[k] for k in row})


def student_list(config, group):
    stud_csv = students_csv(config, group)
    students = []

    with open(stud_csv, 'r') as infile:
        reader = csv.DictReader(infile, students_csv_fieldnames(), KEY_INVALID, strict=True)

        headers = next(reader, None)
        if not validate_headers(headers):
            click.secho('Malformed file: %s. Invalid headers!' % stud_csv)
            exit(1)

        for row in reader:
            if KEY_INVALID in row:
                click.secho('Malformed file: %s' % stud_csv, fg='red')
                exit(1)

            if not check_row(row):
                click.secho('Malformed file: %s. Missing column(s)!' % stud_csv, fg='red')
                exit(1)

            students += [row[KEY_STUDENT_ID]]
    return students


def student_info(config, group):
    stud_csv = students_csv(config, group)
    students = {}

    with open(stud_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, students_csv_fieldnames(), KEY_INVALID, strict=True)

        headers = next(reader, None)
        if not validate_headers(headers):
            click.secho('Malformed file: %s. Invalid headers!' % stud_csv)
            exit(1)

        for row in reader:
            if KEY_INVALID in row:
                click.secho('Malformed file: %s' % stud_csv, fg='red')
                exit(1)

            if not check_row(row):
                click.secho('Malformed file: %s. Missing column(s)!' % stud_csv, fg='red')
                exit(1)

            students[row[KEY_STUDENT_ID]] = row
    return students


def test_student_info(config, test):
    stud_csv = test_students_csv(config, test)
    students = {}

    with open(stud_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, test_students_csv_fieldnames(), KEY_INVALID, strict=True)

        headers = next(reader, None)
        if not validate_headers(headers):
            click.secho('Malformed file: %s. Invalid headers!' % stud_csv)
            exit(1)

        for row in reader:
            if KEY_INVALID in row:
                click.secho('Malformed file: %s' % stud_csv, fg='red')
                exit(1)

            if not check_row(row):
                click.secho('Malformed file: %s. Missing column(s)!' % stud_csv, fg='red')
                exit(1)

            students[row[KEY_STUDENT_ID]] = row
    return students


def tag_group(config, gl, group, tag, verbose):
    students = student_list(config, group)

    errors = []

    with click.progressbar(students, label='Tagging projects') as bar:
        for student_id in bar:
            repo = ue_repo(config, student_id)
            # tag latest commit
            if not tag_project(gl, repo, tag, verbose):
                errors += [student_id]

    return students


class Action(Enum):
    ADD = 1
    DELETE = 2
    MODIFY = 3


class FileInfoFile:

    def __init__(self, path, action, push):
        self.path = path
        self.action = action
        self.push = push


class FileInformation:

    def __init__(self, name):
        self.name = name
        self.files = {}

    def add_file(self, file_path, action, push=False):
        """

        :type action: Action
        :type file_path: basestring
        :type push: bool
        """
        self.files[file_path] = FileInfoFile(file_path, action, push)

    def print_info(self,
                   print_info=lambda x: click.echo(x),
                   print_warn=lambda x: click.secho(x, fg = 'yellow', bold = True),
                   print_add=lambda x, push: click.secho('\tadd: %s%s' % (x, '*' if push else ''), fg = 'green'),
                   print_modify=lambda x, push: click.secho('\tmod: %s%s' % (x, '*' if push else ''), fg = 'blue'),
                   print_delete=lambda x, push: click.secho('\tdel: %s%s' % (x, '*' if push else ''), fg = 'red')):
        if len(self.files) == 0:
            return
        print_info('Change list [%s]' % self.name)
        lists = {}
        push = False
        for k in self.files:
            v = self.files[k]
            if v.action not in lists:
                lists[v.action] = []
            lists[v.action] += [v]
        for k in lists:
            v = lists[k]
            v.sort(key=lambda x: x.path)
            if k == Action.ADD:
                for f in v:
                    if f.push:
                        push = True
                    print_add(f.path, f.push)
            elif k == Action.MODIFY:
                for f in v:
                    if f.push:
                        push = True
                    print_modify(f.path, f.push)
            elif k == Action.DELETE:
                for f in v:
                    if f.push:
                        push = True
                    print_delete(f.path, f.push)
        if push:
            print_warn('*commit and push changes')

    def info_string(self):
        result = []
        self.print_info(
            print_info=(lambda x: result.append('%s' % x)),
            print_warn=(lambda x: result.append('%s' % x)),
            print_add=(lambda x, push: result.append('\t+ %s%s' % (x, '*' if push else ''))),
            print_modify=(lambda x, push: result.append('\t~ %s%s' % (x, '*' if push else ''))),
            print_delete=(lambda x, push: result.append('\t- %s%s' % (x, '*' if push else '')))
        )
        return '\n'.join(result)

    def open_write(self, file_path, push=False):
        if os.path.exists(file_path):
            self.add_file(file_path, Action.MODIFY, push)
        else:
            self.add_file(file_path, Action.ADD, push)

    def delete(self, file_path, push=False):
        if file_path in self.files and self.files[file_path].action == Action.ADD:
            del self.files[file_path]
        else:
            self.add_file(file_path, Action.DELETE, push)


class GuiMode(Enum):
    Exercise = 1,
    Test = 2


class AttendanceType(Enum):
    ATTENDED = 1
    ABSENT = 2
    NOT_SET = 3