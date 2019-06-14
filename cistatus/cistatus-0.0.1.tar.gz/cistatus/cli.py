import logging
import json
import argparse
import os
import re
import requests

try:
    from .providers import find_ci_provider
except ImportError:
    from providers import find_ci_provider

GITHUB_BASE = os.environ.get("GITHUB_BASE", "https://api.github.com")
GITHUB_STATUS_URL = GITHUB_BASE + "/repos/{repo_name}/statuses/{sha}?access_token={token}"
JOB_STATES = ('pending', 'success', 'error', 'failure')
ACTIVE_CI = find_ci_provider()
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def update_status(repo_name, sha, state, desc='CI Status', target_url=None, context="default", token="CI Status"):
    url = GITHUB_STATUS_URL.format(repo_name=repo_name, sha=sha, token=token)
    params = dict()
    if desc:
        params['description'] = desc
    if state:
        params["state"] = state
    if target_url:
        params["target_url"] = target_url
    if context:
        params["context"] = context

    headers = {"Content-Type": "application/json"}
    LOGGER.debug("Setting status on %s %s to %s", repo_name, sha, state)
    result = requests.post(url, data=json.dumps(params), headers=headers)
    LOGGER.debug("Response: %s", result.status_code)
    return result.status_code in [200, 201]


def is_not_none(func):
    def wrapper(*args, **kwargs):
        if args[0]:
            return func(*args, **kwargs)
        raise ValueError()

    return wrapper


@is_not_none
def valid_repo_name(val):
    part = r"[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}"
    full = f"^{part}\/{part}$"
    matcher = re.compile(full)
    if matcher.match(val):
        return val
    raise ValueError()


@is_not_none
def valid_sha(val):
    part = r"[0-9a-f]{5,40}"
    full = f"^{part}$"
    matcher = re.compile(full)
    if matcher.match(val):
        return val
    raise ValueError()


@is_not_none
def valid_pr(val):
    try:
        int(val)
        return val
    except ValueError:
        raise


@is_not_none
def valid_token(val):
    part = r"[0-9a-f]{40}"
    full = f"^{part}$"
    matcher = re.compile(full)
    if matcher.match(val):
        return val
    raise ValueError()


def main():
    parser = argparse.ArgumentParser(description='Set Build Status')
    parser.add_argument('--repo', required=True, type=valid_repo_name, help="user/repo", action=EnvDefault, envvar=ACTIVE_CI.REPO_ENV)
    parser.add_argument('--sha', required=True, type=valid_sha, action=EnvDefault, envvar=ACTIVE_CI.SHA_ENV)
    parser.add_argument('--pr', required=True, type=valid_pr, action=EnvDefault, envvar=ACTIVE_CI.PR_ENV)
    parser.add_argument('--token', required=True, type=valid_token, help="Github API Token", action=EnvDefault, envvar="GITHUB_ACCESS_TOKEN")
    parser.add_argument('--status', choices=JOB_STATES, required=True)
    parser.add_argument('--url', help="Job url")
    parser.add_argument('--description', help="Job Description", default="CI Status")
    parser.add_argument('--context', help="Job context", default="default")

    args = parser.parse_args()

    result = update_status(args.repo, args.sha, args.status, desc=args.description, target_url=args.url, context=args.context, token=args.token)
    LOGGER.info("Succeeded: %s", result)


if __name__ == '__main__':
    main()
