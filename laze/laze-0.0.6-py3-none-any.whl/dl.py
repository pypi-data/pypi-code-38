import os
import subprocess
import json

from laze.common import InvalidArgument
from shutil import rmtree, copytree


queue = {}


def state_filename(target):
    return os.path.join(target, ".laze-dl.yml")


def write_state(source, target):

    with open(state_filename(target), "w") as f:
        json.dump(source, f, indent=4, sort_keys=True)


def read_state(target):
    try:
        with open(state_filename(target), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None


def git_clone(source, target, commit=None):
    if os.path.isdir(os.path.join(target, ".git")):
        if read_state(target) == source:
            # TODO: let git confirm the checkout is in pristine state
            print(
                'laze: not cloning "%s" to "%s", target already exists.'
                % (source, target)
            )
            return
        else:
            print('laze: cleaning "%s"' % target)
            rmtree(target)

    print('laze: cloning "%s" to "%s"' % (source, target))

    if source.startswith("~"):
        source = os.path.expanduser(source)

    subprocess.check_call(["git", "clone", source, target])

    if commit is not None:
        print('laze: setting "%s" to commit %s' % (target, commit))
        subprocess.check_call(["git", "-C", target, "reset", "--hard", commit])

    write_state(source, target)


def add_to_queue(download_source, target):
    existing = queue.get(target)
    if existing and (download_source != existing):
        raise InvalidArgument("laze: error: duplicate download target %s" % target)

    queue[target] = download_source


def start():
    for target, source in queue.items():
        error = False
        if type(source) == str:
            if source.startswith("https://github.com/"):
                git_clone(source, target)
            elif source.endswith(".git"):
                git_clone(source, target)
            else:
                error = True

        elif type(source) == dict:
            if "git" in source:
                git = source.get("git")
                url = git.get("url")
                if url is None:
                    raise InvalidArgument(
                        "laze: error: git download source %s is missing url"
                    )
                commit = git.get("commit")
                git_clone(url, target, commit)
            elif "local" in source:
                local = source["local"]
                path = local.get("path")
                if path is None:
                    raise InvalidArgument(
                        "laze: error: local download source %s is missing path"
                    )
                try:
                    rmtree(target)
                except FileNotFoundError:
                    pass

                copytree(path, target)
            else:
                error = True

        if error:
            raise InvalidArgument("laze: error: don't know how to download %s" % source)

    reset()


def reset():
    global queue
    queue = {}
