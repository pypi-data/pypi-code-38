from bleach import config
from bleach.outputs import slack
from bleach.outputs import stdout
from bleach.sourcecontrol import github


def main(owner, repository, primary, secondary):
    # who needs to check the optional parameters?
    missingCommits = github.missingCommits(owner, repository, primary, secondary)
    hasSomethingToSay = False
    badlyFormattedOutput = ""
    # TODO format the output
    TEMPLATE_MISS = "*{repo}*\nprimary branch `{primary}` seems to be missing commits from secondary branch `{secondary}`"
    TEMPLATE_OK = "*{repo}*\nprimary branch `{primary}` seems to be synced with secondary branch `{secondary}`"
    if missingCommits:
        hasSomethingToSay = True
        badlyFormattedOutput = TEMPLATE_MISS.format(repo=repository, primary=primary, secondary=secondary)
    else:
        badlyFormattedOutput = TEMPLATE_OK.format(repo=repository, primary=primary, secondary=secondary)
    outputMethod = config.CONFIG["outputMethod"]
    if hasSomethingToSay or not config.CONFIG['printOnlyActionable']:
        if outputMethod == 'stdout':
            stdout.send(badlyFormattedOutput)
        elif outputMethod == 'slack':
            slack.send(badlyFormattedOutput)
        else:
            raise Exception("invalid output method %s" % outputMethod)
