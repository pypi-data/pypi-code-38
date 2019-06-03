import subprocess

def clone(repo):
    return subprocess.run(["hub", "clone", repo])

def fork():
    return subprocess.run(["hub", "fork"])

def pull_request(message):
    return subprocess.run(["hub", "pull-request", "-m", message, "--base", "ataleek:master"])