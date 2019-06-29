##
#  git.py
#  tagsnag
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 01.11.2018.
#  Copyright (c) 2018 www.geeky.gent. All rights reserved.
#

from .snag import Snag

import os
from shutil import copyfile
from distutils.dir_util import copy_tree
import logging
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from git import Git
from git import Repo
from git.exc import InvalidGitRepositoryError
from git.exc import GitCommandError

from xml.etree import ElementTree as ET


class Git():
    """This class handles file-system / Git related tasks"""

    def __init__(self, path, cpu_count=1):
        super(Git, self).__init__()

        self.cwd = path
        self.cpu_count = cpu_count
        self.initial_setup()
        self.status_map = {}


    def start_with_xml(self, xml_path):
        self.set_xml_path(xml_path)
        self.load_repositories(self.xml_path)

        for snag in self.snags:

            self.checkout(self.repositories[snag.repo_name], 'master')
            self.pull(self.repositories[snag.repo_name])
            self.checkout(self.repositories[snag.repo_name], snag.tag)
            #  self.searchFileName(path=snag.local_repo_path, containing_folder=snag.containing_folder, filenames=[snag.filename], extension=snag.extension)

            found_paths = self.search_files(filename=snag.filename, path=snag.local_repo_path, extension=snag.extension)
            if len(found_paths) > 0:
                self.copy_file_to_destination(path = found_paths[0], destination = snag.destination)


    def active_branch(self, repo):
        """ Return name of active branch or None """

        # Detached state needs to be checked first or repo.active_branch will crash
        if repo.head.is_detached:
            return None
        else:
            return "{}".format(repo.active_branch)


    def head_state(self, repo):
        """ Return human readable description of head location """

        active_tag = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)

        if active_tag:
            return active_tag

        # Detached state needs to be checked first or repo.active_branch will crash
        if repo.head.is_detached:
            commit_string = '{}'.format(repo.head.commit)
            return 'Detached at {}'.format(commit_string[:7])

        active_branch = self.active_branch(repo)


        if active_branch:
            return active_branch


    def update_all_repos(self):
        """Initiate threaded updates for all repositories in working directory"""

        if not self.repos:
            self.repos = self.collect_repositories(self.cwd)

        self.update_repos(self.repos)


    def update_repos(self, repos):

        self.log.info('Initiating repo update on up to {} threads.'.format(self.cpu_count))

        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            for repo in self.repos:
                executor.submit(self.update_repo, repo)


    def update_repo(self, repo):
        """Update provided repository"""

        repo_path = self.get_root(repo)
        repo_name = os.path.basename(repo_path)

        self.log.info('[{}]: Checking status.'.format(repo_name))

        if self.is_dirty(repo):
            self.log.info('  [{}]: Dirty repository detected.'.format(repo_name))
            if self.should_autostash:
                self.log.info('    [{}]: Autostash enabled. Stashing...'.format(repo_name))
                self.stash_repo(repo)

            else:
                self.log.info('    [{}]: Autostash disabled. Skipping...'.format(repo_name))
                return
        else:
            self.log.debug('  [{}]: Status clean.'.format(repo_name))


        self.log.info('[{}]: Initiating update...'.format(repo_name))

        self.checkout(repo, 'master')
        self.pull(repo)


    def find_tag(self, repo, keyword):
        """Attempt to find tag in provided repo. Fallback to fuzzyfind tag"""

        found_tag = ""

        # newest tags first — tags are in arbitrary order, therefore 1. sort, 2. reverse
        #  tags = reversed(sorted(repo.tags, key=lambda t: t.tag.tagged_date))
        tags = repo.tags
        repo_name = self.get_repo_name(repo)

        self.log.info('[{}]: Searching for tag: <{}>'.format(repo_name, keyword))

        self.log.debug('  [{}]: List of tags:{}'.format(repo_name, tags))

        # check if keyword corresponds to one tag exactly
        if keyword in tags:
            self.log.debug('  [{}]: <{}> matched exactly'.format(repo_name, keyword))
            found_tag = keyword
        else:
            self.log.debug('  [{}]: Couldn\'t find {}. Fuzzy search... '.format(repo_name, keyword))
            for tag in tags:
                if keyword in str(tag):
                    found_tag = tag
                    self.log.debug('    [{}]: Fuzzy matched {} > <{}>.'.format(repo_name, keyword, found_tag))

        return found_tag


    def clone_url_into_path(self, url, path):
        """ Clones from a url into the provided path """
        Repo.clone_from(url, path)


    def assign_master_repo(self, master_path, repo_url, remote_name, keep_remote=False):
        """ If provided master path is a repository, the repo_url is added as remote
            and the content of the master repo pushed to the remote """

        if self.is_git_dir(master_path):
            master_repo = Repo(master_path)

            remote = master_repo.create_remote(remote_name,
                                      url=repo_url)

            remote.push(refspec='{}:{}'.format('master',
                                               'master'))

            if not keep_remote:
                # Delete the remote post-push
                assert not master_repo.delete_remote(remote).exists()


    def extract_directory_from_all_repos(self, tag, directory, destination):
        """Initiate threaded directory extraction for all repositories in working directory"""

        if not self.repos:
            self.repos = self.collect_repositories(self.cwd)

        self.extract_directory_from_repos(repos = self.repos,
                                          tag = tag,
                                          directory = directory,
                                          destination = destination)


    def extract_directory_from_repos(self, repos, tag, directory, destination):
        """Initiate threaded directory extraction for all repositories in working directory"""

        self.log.info('Initiating directory extraction on {} threads.'.format(self.cpu_count))

        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            for repo in repos:
                # self.status_map[repo] = 'Extract {} -> {}. Tag: {}'.format(directory, destination, tag)
                self.status_map[repo] = False
                executor.submit(self.extract_directory, repo, tag, directory, destination)


    def extract_directory(self, repo, tag, directory, destination):
        """Attempt to extract described directory from provided repo"""

        repo_path = self.get_root(repo)
        repo_name = os.path.basename(repo_path)

        valid_tag = self.find_tag(repo, tag)

        if valid_tag == '':
            self.log.info('  [{}]: <{}> tag could not be found. Skipping repo'.format(repo_name, tag))
            return

        else:
            self.log.info('  [{}]: Valid Tag found: {} -> {}'.format(repo_name, tag, valid_tag))


        self.checkout(repo, valid_tag)

        found_paths = self.search_directory(directory=directory, path=repo_path)

        if len(found_paths) > 0:
            self.copy_directory_to_destination(path = found_paths[0], destination = os.path.join(destination, repo_name))
            self.status_map[repo] = True


    def extract_file_from_all_repos(self, tag, filename, extension, destination):
        """Initiate threaded file extraction for all repositories in working directory"""

        if not self.repos:
            self.repos = self.collect_repositories(self.cwd)

        self.extract_file_from_repos(repos = self.repos,
                                     tag = tag,
                                     filename = filename,
                                     extension = extension,
                                     destination = destination)


    def extract_file_from_repos(self,repos, tag, filename, extension, destination):
        """Initiate threaded file extraction for all repositories in working directory"""

        self.log.info('Initiating file extraction on {} threads.'.format(self.cpu_count))

        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            for repo in repos:
                executor.submit(self.extract_file, repo, tag, filename, extension, destination)


    def extract_file(self, repo, tag, filename, extension, destination):
        """Attempt to extract described file from provided repo"""

        repo_path = self.get_root(repo)
        repo_name = os.path.basename(repo_path)

        valid_tag = self.find_tag(repo, tag)
        if valid_tag == '':
            self.log.info('  [{}]: <{}> tag could not be found. Skipping repo'.format(repo_name, tag))
            return
        else:
            self.log.info('  [{}]: Valid Tag found: {} -> {}'.format(repo_name, tag, valid_tag))

        self.checkout(repo, valid_tag)
        found_paths = self.search_files(filename=filename,
                path=repo_path,
                extension=extension)

        if len(found_paths) > 0:
            self.copy_file_to_destination(path = found_paths[0], destination = os.path.join(destination, repo_name + '.' + extension))


    def start(self):
        self.load_repositories(self.xml_path)

        for snag in self.snags:

            self.checkout(self.repositories[snag.repo_name], 'master')
            self.pull(self.repositories[snag.repo_name])
            self.checkout(self.repositories[snag.repo_name], snag.tag)
            #  self.searchFileName(path=snag.local_repo_path, containing_folder=snag.containing_folder, filenames=[snag.filename], extension=snag.extension)

            found_paths = self.search_files(filename=snag.filename,
                    path=snag.local_repo_path,
                    extension=snag.extension)

            if len(found_paths) > 0:
                self.copy_file_to_destination(path = found_paths[0], destination = snag.destination)


    def initial_setup(self):
        # Instance variable init
        self.snags = []
        self.repos = []
        self.repo_names_and_urls = {}
        self.repositories = {}

        ##
        # Flags
        self.should_prune = False
        self.should_autostash = False
        self.verbose = False
        self.should_create_logfile = False

        # Advanced setup
        self.setup_logger()


    def enable_logfile(self):

        if self.log:
            # Create filehandler
            fh = logging.FileHandler('Tagsnag.log')
            fh.setLevel(logging.DEBUG)
            self.log.addHandler(fh)


    def setup_logger(self):
        """ Creating / configuring logger instance """

        logging.basicConfig(level=logging.WARNING, format='%(msg)s')
        self.log = logging.getLogger('logger')


        ##
        # Setting up argument parser
        self.log.debug('Setting up argument parser...')


    ##
    # XML methods

    def set_xml_path(self, path):
        """ XML Path Setter """

        self.log.debug('Provided Path: {}'.format(path))
        self.xml_path = path
        self.generate_snag_from_xml_path(path)


    def generate_snag_from_xml_path(self, path):
        """ Ingests XML from provided path """

        self.log.debug('Attempting to parse xml file: {}'.format(path))

        doc = ET.parse(path).getroot()

        for repo in doc.findall('repository'):
            url = repo.find('./url').text.strip().rstrip()

            # create repo name by converting to norm path, extracting basepath and cutting off before the .git extension
            repo_name = os.path.basename(os.path.normpath(url)).split('.')[0]
            repo_path = os.path.normpath("{}/{}".format(os.path.dirname(path), repo_name))
            self.repo_names_and_urls[repo_name]=url
            self.log.debug('Repository: {}'.format(url))

            for snag in repo.findall('snag'):
                tag = snag.find('tag').text.strip().rstrip()
                containing_folder = snag.find('folder').text.strip().rstrip()
                filename = snag.find('filename').text.strip().rstrip()
                extension = snag.find('extension').text.strip().rstrip()
                destination = snag.find('destination').text.strip().rstrip()
                destination = os.path.join(destination + containing_folder, repo_name + '.' + extension)

                s = Snag(url=url,
                        tag=tag,
                        repo_name=repo_name,
                        local_repo_path=repo_path,
                        containing_folder=containing_folder,
                        filename=filename,
                        extension=extension,
                        destination=destination)

                self.snags.append(s)
                self.log.debug('Tag: {}\nFilename: {}\nextension: {}\nDestination: {}\n'.format(tag, filename, extension, destination))

            self.log.debug('Extracted Snags: {}'.format(self.snags))
            self.log.info('Extracted Repositories: {}'.format(self.repo_names_and_urls))


    ##
    # Git methods

    def clone_repository(self, destination, url):
        """ Clones repository from url into root destination folder """

        self.log.info('Cloning from {}\ninto {}'.format(url, destination))
        self.log.info('--- This feature is not implemented yet ---')

        #  Repo.clone_from(url, destination)

        #  p = subprocess.Popen(['git', 'clone', url], cwd=destination)
        #  p.wait()

        #  ssh_executable = os.path.join('.', 'ssh_executable.sh')
        #  with Git().custom_environment(GIT_SSH=ssh_executable):
            #  Repo.clone_from(url, destination)


        # Somehow doesnt work properly?
        #  git_ssh_identity_file = os.path.expanduser('~/.ssh/github')
        #  git_ssh_cmd = 'ssh -i {}'.format(git_ssh_identity_file)
        #  with Git().custom_environment(GIT_SSH_COMMND=git_ssh_cmd):
            #  Repo.clone_from(url, destination)


    def checkout(self, repo, target):
        """ Checkout provided target within given repository """

        self.log.debug('Checking out {} in {}'.format(target, self.get_root(repo)))
        git = repo.git
        git.checkout(target)


    def pull(self, repo):
        """ Pull origin / master for provided repository """
        repo_name = self.get_repo_name(repo)

        self.log.debug('  [{}]: Pulling origin/master'.format(repo_name))
        git = repo.git

        if self.should_prune:
            git.pull('origin', 'master')
            git.pull('origin', '--tags')

        else:
            git.pull('origin', 'master', '--prune')
            git.pull('origin', '--tags', '--prune')


    def is_dirty(self, repo):
        """ Returns True if repository status is dirty """

        try:
            diff_results = repo.index.diff(repo.head.commit)

        except ValueError as exception:
            diff_results = repo.index.diff(None)

        else:
            if len(diff_results) == 0:
                diff_results = repo.index.diff(None)

        return (len(diff_results) > 0)


    def stash_repo(self, repo):
        """ Run stash within provided repository """

        assert repo
        git = repo.git
        git.stash()


    def stash_pop_repo(self, repo):
        """ Run stash within provided repository """

        assert repo.exists()
        git = repo.git
        git.stash('pop')


    def get_root(self, repo):
        return repo.git.rev_parse('--show-toplevel')


    def fetch(self, repo, progress_printer = None):
        """ Fetch data from origin for provided repo and branch and return fetch info """

        fetch_info = None
        repo_name = self.get_repo_name(repo)
        self.log.debug('  [{}]: Fetch initiated'.format(repo_name))
        try:
            if progress_printer == None:
                fetch_info = repo.remotes.origin.fetch()

            else:
                origin = repo.remotes.origin
                assert origin.exists()
                fetch_info = origin.fetch(progress=progress_printer)

        except GitCommandError as exception:
            self.log.info('  [{}]: Git Command Error:\n{}'.format(repo_name, exception))

            if exception.stdout:
                self.log.info('  [{}]: !! stdout was:'.format(repo_name))
                self.log.info('  [{}]: {}'.format(repo_name, exception.stdout))

            if exception.stderr:
                self.log.info('  [{}]: !! stderr was:'.format(repo_name))
                self.log.info('  [{}]: {}'.format(repo_name, exception.stderr))
        # except AssertionError as exception:
        #     print('exception {}'.format(exception))

        return fetch_info


    def merge(self, repo, source_branch_name, target_branch_name):
        repo_name = self.get_repo_name(repo)
        print('{}: Merge {} into {}'.format(repo_name, source_branch_name, target_branch_name))
        try:
            git = repo.git
            git.execute(['git', 'checkout', '{}'.format(target_branch_name)])
            git.execute(['git', 'merge', '{}'.format(source_branch_name), '--ff-only'])

        except GitCommandError as exception:

            self.log.info('  [{}]: Git Command Error:\n{}'.format(repo_name, exception))

            if exception.stdout:
                self.log.info('  [{}]: {}'.format(repo_name, exception.stdout))
                self.log.info('  [{}]: !! stdout was:'.format(repo_name))

            if exception.stderr:
                self.log.info('  [{}]: !! stderr was:'.format(repo_name))
                self.log.info('  [{}]: {}'.format(repo_name, exception.stderr))

        # Solution using GitPython. Saved as reference
        # source = repo.branches[source_branch_name]
        # assert source

        # target = repo.branches[target_branch_name]
        # assert target

        # base = repo.merge_base(source, master)
        # assert base

        # repo.index.merge_tree(target, base=base)
        # repo.index.commit('Merge {} into {}'.format(source_branch_name, target_branch_name), parent_commits=(source.commit, target.commit))



    def behind_branch(self, repo, remote, branch):
        """ Checks by how many commits <branch> is behind <remote>/<branch> """

        # print('[{}]: BEHIND? Branch: {} Remote: {}'.format(self.get_repo_name(repo), branch, remote))
        return int(repo.git.rev_list('--left-only', '--count', '{}/{}...@'.format(remote, branch)))


    def ahead_branch(self, repo, remote, branch):
        """ Checks by how many commits <branch> is ahead <remote>/<branch> """

        # print('[{}]: AHEAD? Branch: {} Remote: {}'.format(self.get_repo_name(repo), branch, remote))
        return int(repo.git.rev_list('--right-only', '--count', '{}/{}...@'.format(remote, branch)))


    ##
    # Filesystem methods

    def collect_repositories(self, path):
        repos = []

        self.log.debug('DETECT REPOSITORIES IN PATH: {}'.format(path))

        with os.scandir(path) as dirnames:
            for sub_dir in dirnames:
                # print('path {}'.format(path))
                # print('sub {}'.format(sub_dir))

                if not path == None:
                    repo_path = os.path.join(path, sub_dir)

                else:
                    repo_path = os.path.join('./',sub_dir)

                if self.is_git_dir(repo_path):
                    repos.append(Repo(repo_path))

        return repos


    def load_repositories(self, path):
        """ Checks existence of repository paths and initiates clone """
        destination_path = os.path.dirname(path)
        for repo_name in self.repo_names_and_urls:
            url = self.repo_names_and_urls[repo_name]
            repo_path = os.path.normpath("{}/{}".format(destination_path, repo_name))
            self.log.debug(repo_path)
            if os.path.exists(repo_path):
                self.log.info('[{}]: Repository exists.'.format(repo_name))

                repo = Repo(repo_path)
                assert not repo.bare
                self.repositories[repo_name] = repo

            else:
                self.log.info('[{}]: Repository does not exist. Attempting to clone it...'.format(repo_name))
                # @todo: Implement
                #  self.clone_repository(destination=repo_path, url=url)


    def search_directory(self, directory, path='.'):
        normalized_dirname = directory.lower()
        found_paths = []

        for dirpath, dirnames, files in os.walk(path):

            # Skip .git folder
            if ".git" in dirpath:
                continue

            if normalized_dirname in dirpath.lower():
                self.log.info('Found Directory {}'.format(dirpath))
                found_paths.append(dirpath)

        return found_paths


    def search_files(self, filename, path='.', extension=''):
        extension = extension.lower()
        found_paths = []

        for dirpath, dirnames, files in os.walk(path):

            # Skip .git folder
            if ".git" in dirpath:
                continue

            for file in files:
                if extension and file.lower().endswith(extension):
                    if filename.lower() in file.lower():
                        foundPath = os.path.join(dirpath, file)
                        self.log.info('Found {}'.format(foundPath))
                        found_paths.append(foundPath)
                #  elif not extension:
                    #  print(os.path.join(dirpath, file))
        return found_paths


    def copy_file_to_destination(self, path, destination):
        self.log.info('Copying from:\n{}\nto:\n{}'.format(path, destination))

        if os.path.exists(path):

            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination))
            try:
                copyfile(path, destination)
            except IOError:
                self.log.info(IOError.message)
        else:
            self.log.info('File does not exist. Aborting...')


    def copy_directory_to_destination(self, path, destination):
        self.log.info('Copying from:\n{}\nto:\n{}'.format(path, destination))

        if os.path.exists(path):

            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination))
            try:
                copy_tree(path, destination)
            except IOError:
                self.log.info(IOError.message)
        else:
            self.log.info('File does not exist. Aborting...')


    ##
    # Helper methods

    def is_git_dir(self, path):
        """ Returns True if path contains valid Git repo """

        try:
            Repo(path)
            return True
        except InvalidGitRepositoryError:
            return False


    def get_repo_name(self, repo):
        """ Returns name of provided repo """

        repo_path = self.get_root(repo)
        repo_name = os.path.basename(repo_path)
        return repo_name


    ##
    # Setter and getter

    def set_verbose(self, flag):
        """ Verbose Flag Setter """
        self.verbose = flag

        if flag:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)


    def set_should_prune(self, flag):
        """ Should Prune Setter """

        self.should_prune = flag


    def set_should_autostash(self, flag):
        """ Autostash Setter """

        self.should_autostash = flag


    def set_create_logfile(self, flag):
        """ Create Logfile Setter """

        self.should_create_logfile = flag

        if flag:
            self.enable_logfile()

