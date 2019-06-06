import base64
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
            print("couldn't find the organization or repository")
            return []

        if response.status_code == 401:
            print("unauthorized, check your username or password")
            raise Exception("unauthorized, check your username or password")

        processedResponse = response.json()
        pullrequests = processedResponse['values']
        processedResults.extend(
            pullrequest.PullRequest(
                repo=repository,
                createdAt=pullrequestInfo['created_on'],
                user=pullrequestInfo['author']['username'],
                title=pullrequestInfo['title'],
            )
            for pullrequestInfo in pullrequests
        )

        if 'next' in processedResponse:
            url = processedResponse['next']
        else:
            keepFetchingResults = False

    return processedResults


def _getUrl(owner, repository):
    URL_TEMPLATE = "https://api.bitbucket.org/2.0/repositories/{owner}/{repository}/pullrequests{params}"
    params = "?state=OPEN"
    url = URL_TEMPLATE.format(owner=owner, repository=repository, params=params)
    return url


def _getHeaders():
    headers = {}
    authorizationString = "{username}:{password}".format(
        username=config.CONFIG["bitbucketCloudUser"], password=config.CONFIG["bitbucketCloudPassword"])
    encodedAuthorizationString = base64.b64encode(bytes(authorizationString, 'utf-8'))
    headers["Authorization"] = "basic %s" % encodedAuthorizationString.decode('utf-8')
    return headers
