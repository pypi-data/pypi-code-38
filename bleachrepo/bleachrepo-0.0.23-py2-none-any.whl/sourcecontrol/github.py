import requests

from bleach import config
from bleach.models import pullrequest


def listPullRequests(owner, repository):
    url = _getUrl(owner, repository)
    headers = _getHeaders()
    processedResults = []

    keepFetchingResults = True
    while keepFetchingResults:
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise Exception("couldn't find the organization or repository")

        if response.status_code == 401:
            raise Exception("unauthorized, check your access token")

        pullrequests = response.json()

        def getLogin(user):
            return user['login']

        for pullrequestInfo in pullrequests:
            if 'assignees' in pullrequestInfo and len(pullrequestInfo['assignees']):
                user = ', '.join(map(getLogin, pullrequestInfo['assignees']))
            else:
                user = getLogin(pullrequestInfo['user'])

            processedResults.append(
                pullrequest.PullRequest(
                    repo=repository,
                    createdAt=pullrequestInfo['created_at'],
                    user=user,
                    title=pullrequestInfo['title'],
                    url=pullrequestInfo['html_url'],
                )
            )

        if response.links and 'next' in response.links:
            url = response.links['next']['url']
        else:
            keepFetchingResults = False

    return processedResults


# alert if there's a commit in `branchSecondary` that isn't in `branchPrimary`
# also consider how old that commit is
def missingCommits(owner, repo, branchPrimary, branchSecondary):
    URL_TEMPLATE = "https://api.github.com/repos/{owner}/{repo}/commits?sha={branch}"
    headers = _getHeaders()

    roleToBranch = {
        'primary': {'name': branchPrimary},
        'secondary': {'name': branchSecondary},
    }

    for branch in roleToBranch.values():
        url = URL_TEMPLATE.format(owner=owner, repo=repo, branch=branch['name'])
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise Exception("couldn't find the organization or repository")

        commits = response.json()
        branch['commits'] = commits
        branch['shas'] = [commit['sha'] for commit in commits]

    # heuristics begin here
    if roleToBranch['secondary']['commits'][0]['sha'] not in roleToBranch['primary']['shas']:
        # print(roleToBranch['secondary']['commits'][0]['sha'], 'is not in', roleToBranch['primary']['shas'])
        # care to elaborate on what's missing?
        # also check how long
        return True

    return False


def _getUrl(owner, repository):
    URL_TEMPLATE = "https://api.github.com/repos/{owner}/{repository}/pulls{params}"
    params = "?state=open&sort=created_at&direction=asc"
    url = URL_TEMPLATE.format(owner=owner, repository=repository, params=params)
    return url


def _getHeaders():
    headers = {}
    if config.CONFIG["githubAccessToken"]:
        headers['Authorization'] = 'token ' + config.CONFIG["githubAccessToken"]
    return headers
