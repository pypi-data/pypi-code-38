from bleach import config
from bleach.outputs import slack
from bleach.outputs import stdout
from bleach.sourcecontrol import github
from bleach.formatters import oldest_requests
from bleach.sourcecontrol import bitbucket_cloud

def main(owner, repository):
    sourceControl = config.CONFIG["sourceControl"]
    if sourceControl == 'github':
        pullrequestInfo = github.listPullRequests(owner, repository)
    elif sourceControl == 'bitbucket':
        pullrequestInfo = bitbucket_cloud.listPullRequests(owner, repository)
    else:
        raise Exception("invalid source control %s" % sourceControl)

    formattedOutput = oldest_requests.doFormat(pullrequestInfo)

    outputMethod = config.CONFIG["outputMethod"]
    if outputMethod == 'stdout':
        stdout.send(formattedOutput)
    elif outputMethod == 'slack':
        slack.send(formattedOutput)
    else:
        raise Exception("invalid output method %s" % outputMethod)
