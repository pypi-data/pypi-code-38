import os
import sys
import filecmp
import getpass
from urllib.parse import quote

from . import configs
from . import paths as path_helpers
from odoo_manager.core import shell

pipe_dev_null = path_helpers.pipe_dev_null


def redirect(verbose=False):
    """
    :param verbose {bool}:
    :return {str}:
    """
    return "" if verbose else (" " + pipe_dev_null)


class console_colors(object):
    """
    Helper to hold some constant for shell colors.
    """

    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def print_diff_files(ctx, dcmp):
    """
    :param ctx {invoke.context.Context}: Invoke context variable
    :param dcmp:
    :return {NoneType}:
    """
    for name in dcmp.diff_files:
        print(
            console_colors.WARNING
            + "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
            + console_colors.ENDC
        )
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(ctx, sub_dcmp)


def _git_clone(ctx, url, branch, output, depth=1):
    """
    Does a system call on git clone, returns the exit status from that system.

    :param url {str}:
    :param branch {str}:
    :return {int}: Returns int representing success or failure
    """
    return ctx.run(
        "git clone {url} {output} --branch={branch} --depth={depth} --quiet{pipe}".format(
            url=url, branch=branch, output=output, depth=depth, pipe=redirect()
        )
    )


def _get_git_config():
    git_config = {}
    # Right now, just assuming github.com repos
    if not configs.config.has_option("options", "USERNAME") or not configs.config.has_option("options", "PASSWORD"):
        git_config["username"] = quote(input("Github username? "))
        git_config["password"] = quote(getpass.getpass("Github password? "))
    else:
        git_config["username"] = configs.config.get("options", "USERNAME")
        git_config["password"] = configs.config.get("options", "PASSWORD")
    return git_config


def _get_git_urls(repo_url):
    if repo_url[:4] == "http":
        http_url = repo_url
        ssh_url = (
            repo_url.replace("https://", "git@")
            .replace("http://", "git@")
            .replace(".com/", ".com:")
            .replace(".org/", ".org:")
        )
    else:
        ssh_url = repo_url
        http_url = repo_url.replace("git@", "https://").replace(".com:", ".com/").replace(".org:", ".org/")

    return {"ssh": ssh_url, "http": http_url}


def git_clone(ctx, url, branch, repo_name, output, depth=1):
    urls = _get_git_urls(url)
    try:
        shell.out("        *Trying to clone {}...".format(urls["ssh"]), color="yellow")
        _git_clone(ctx, urls["ssh"], branch, output, depth=depth)
    except:
        try:
            shell.out("        *Trying to clone {}...".format(urls["http"]), color="yellow")
            _git_clone(ctx, urls["http"], branch, output, depth=depth)
        except:
            try:
                credentials = _get_git_config()
                credentials_url = "https://{username}:{password}@{url}".format(
                    username=credentials.get("username"), password=credentials.get("password"), url=urls["http"][8:]
                )
                shell.out("        *Trying to clone {}...".format(credentials_url), color="yellow")
                _git_clone(ctx, credentials_url, branch, output, depth=depth)
            except:
                shell.out("        Sorry, could not clone the repo {}".format(repo_name), color="red")


def diff_dependency_git(ctx, name, module_config, log=True):
    """
    :param name:
    :param module_config:
    :return: dict Paths for the modules
    """
    paths = path_helpers.Paths()

    if log:
        shell.out("  Processing {}...".format(name), color="yellow")

    repo_name = module_config["url"].replace(".git", "").split("/").pop()
    repo_temp_path = paths.base("_make_tmp/{}".format(repo_name))
    original_path = paths.base("_lib/{}".format(name))

    # If there is no repo cloned down into the temp folder yet, then we are going to git clone it
    # down so that we can access modules that we need to move into _lib.
    if not os.path.isdir(repo_temp_path):
        shell.out("    *Starting git clone for {}...".format(module_config["url"]), color="yellow")

        repo_url = module_config["url"]
        repo_branch = module_config["branch"]
        git_clone(ctx, repo_url, repo_branch, repo_name, output=paths.base("_make_tmp/{}".format(repo_name)))

    # Once we've got the modules and files setup, then we are going to check and see if we want
    # to run a diff on these these or not.
    if os.path.isdir(paths.base("{temp_path}/{module_name}".format(temp_path=repo_temp_path, module_name=name))):
        temp_module_path = paths.base("{temp_path}/{module_name}".format(temp_path=repo_temp_path, module_name=name))
        if log and os.path.isdir(original_path):
            print_diff_files(ctx, filecmp.dircmp(original_path, temp_module_path))
    else:
        shell.out(
            " ** Unable to find {module_name} in {repo}.".format(repo=module_config["url"], module_name=name),
            color="red",
        )
        exit(1)

    return {"original": original_path, "updated": temp_module_path}


def diff_dependency(ctx, name, module_config, log=True):
    """
    :param ctx {invoke.context.Context}: Invoke context variable
    :param name {str}:
    :param module_config:
    :return {NoneType}:
    """
    if "type" in module_config:
        fn = getattr(sys.modules[__name__], "diff_dependency_{type}".format(type=module_config["type"]))
        if fn:
            return fn(ctx, name, module_config, log)
    else:
        return diff_dependency_git(ctx, name, module_config, log)


def update_dependency(ctx, name, module_config):
    """
    :param ctx {invoke.context.Context}: Invoke context variable
    :param name {str}:
    :param module_config:
    :return {NoneType}:
    """
    diff_paths = diff_dependency(ctx, name, module_config, log=False)
    shell.out("  Updating lib with {}...".format(os.path.basename(diff_paths["original"])), color="yellow")
    os.system("rm -rf {}".format(diff_paths["original"]))
    os.system("cp -R {} {}".format(diff_paths["updated"], diff_paths["original"]))
