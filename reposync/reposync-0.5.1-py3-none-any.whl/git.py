import git

from .commander import Commander


class Git:
    def __init__(self, config):
        self.commander = Commander(config)

        self.gopath = config.get("gopath")
        self.method = config.get("method")

    def clone(self, repository):
        if repository.kind == "go":
            link_name = repository.path
            target = self.prepend_gopath(repository.url)
            self.commander.ln(target, link_name)

            repository.path = target

        print("Cloning", repository.path, "...")
        try:
            git.Repo.clone_from(self.get_clone_url(repository.url), repository.path)
        except git.exc.GitCommandError:
            print("Skipped cloning", repository.path)
        else:
            print("Cloned", repository.path)

    def pull(self, repository):
        if repository.kind == "go":
            repository.path = self.prepend_gopath(repository.url)

        print("Pulling", repository.path, "...")
        try:
            git.Git(repository.path).pull()
        except git.exc.GitCommandError:
            print("Failed pulling", repository.path)
        else:
            print("Pulled", repository.path)

    # private

    def get_clone_url(self, repository_url):
        if self.method == "https":
            return self.convert_to_https_url(repository_url)
        if self.method == "ssh":
            return self.convert_to_ssh_url(repository_url)

    def convert_to_https_url(self, repository_url):
        return "https://" + repository_url + ".git"

    def convert_to_ssh_url(self, repository_url):
        url_splits = repository_url.split("/")
        host, path = url_splits[0], "/".join(url_splits[1:])
        return "git@" + host + ":" + path + ".git"

    def prepend_gopath(self, repository_url):
        return "{}/src/{}".format(self.gopath, repository_url)
