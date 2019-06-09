import svn.remote
import logging
import hashlib

logger = logging.getLogger(__name__)

class VCSWatchClient(object):
    '''
    Represents a generic Version Control System client that will be used
    by VCSWatch.
    '''

    url      = None
    username = None
    password = None

    def set_url(self, url):
        '''
        Remoter repository URL
        '''
        self.url = url

    def set_username(self, username):
        '''
        Username for remote repository authentication
        '''
        self.username = username

    def set_password(self, password):
        '''
        Password for remote repository authentication
        '''
        self.password = password

    def __str__(self):
        return 'VCSWatchClient<{:s}>'.format(self.url)

    def init(self):
        '''
        Initiate the remote repository client using the `url`, `username` and
        `password` provided from the other methods.
        '''
        pass
    
    def get_lastest_revision(self):
        '''
        Return the lastest revision from the root of the remote repository.
        This could also be a commit hash (ie: git). The important thing is
        that this bit of information be unique to represent a known state
        of the repository.
        '''
        return None
    
    def get_hash(self):
        return None

class VCSWatchClientSVN(VCSWatchClient):
    '''
    Implements a VCSWatchClient for Subversion.
    '''

    svnclient = None

    def init(self):
        if not self.username and self.password:
            self.svnclient = svn.remote.RemoteClient(url=self.url, username=self.username, password=self.password)
        else:
            self.svnclient = svn.remote.RemoteClient(url=self.url)

    def get_lastest_revision(self):
        info = self.svnclient.info()
        return info['commit_revision']

    def get_hash(self):
        info = self.svnclient.info()
        return hashlib.sha1(info['url'].encode()).hexdigest()

    # def __str__(self):
    #     return VCSWatchClient.__str__(self)