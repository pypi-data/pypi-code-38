import git
import os
import platform


def geturl(repo):
    """
    Get the origin url if present
    :param repo:
    :return:
    """
    if repo.remotes:
        for remote in repo.remotes:
            if hasattr(remote, "name"):
                name = remote.name
                if name == "origin":
                    url = remote.url
                    if "@" in url and url.startswith("http"):
                        # strip out the username and password
                        protocol, rest = url.split("//", 1)
                        _, address = rest.split("@", 1)
                        url = "{}//{}".format(protocol, address)
                    return url

    return None


def getinfo(folder, package=None):
    """
    Get the system and git information
    :return:
    """
    repo = git.Repo(os.path.abspath(folder))

    info = {
        "repo": geturl(repo),
        "system": platform.system(),
        "arch": platform.machine(),
        "commit": repo.head.object.hexsha,
        "package": package
    }

    return info
