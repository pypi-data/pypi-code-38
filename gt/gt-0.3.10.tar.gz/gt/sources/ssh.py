import subprocess
from .base import GitSource

#TODO use paramiko + improve error handling

class SSH(GitSource):
    def __init__(self, host, user, project_dir):
        self.host = host
        self.user = user
        self.project_dir = project_dir
        self.run = lambda cmd:\
            subprocess.check_output(["ssh", "{0}@{1}".format(user, host), cmd])

    def git_url(self, name):
        return "ssh://{user}@{host}:{path}".format(user=self.user,
                                                host=self.host,
                                                path=self.project_dir + "/" + name)
    
    def create(self, name, is_private=True):
        if not is_private:
            raise Exception("Cannot create public repository on standard SSH source.")
        
        cmd = "cd {projectDir} && mkdir {project} && cd {project} && git init --bare"\
               .format(projectDir=self.project_dir, project=name)
        try:
            self.run(cmd)
        except:
            raise Exception("Failed to create {0}, perhaps it already exists".format(name))
        
                                        
    @property
    def repos(self):
        try:
            repos = self.run("ls " + self.project_dir).decode('utf-8')\
                       .strip()\
                       .split("\n")
            return [(repo, True) for repo in repos]
        except:
            raise Exception("Failed to list {0}, does the project directory exist?"
                            .format(self.project_dir))
        
    def delete(self, name):
        cmd = "cd {projectDir} && rm -r {name}".format(projectDir=self.project_dir, name=name)
        try:
            self.run(cmd)
        except:
            raise Exception("Failed to remove {0}, does it exist?".format(name))
