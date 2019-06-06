import os

DEFAULT_OUTPUT_METHOD = 'stdout'
DEFAULT_SOURCE_CONTROL = 'github'

CONFIG = {
    "slackWebhook": os.environ.get("BLEACH_SLACK_WEBHOOK", None),
    "githubAccessToken": os.environ.get("BLEACH_GITHUB_ACCESS_TOKEN", None),
    "bitbucketCloudUser": os.environ.get("BLEACH_BITBUCKET_CLOUD_USER", None),
    "bitbucketCloudPassword": os.environ.get("BLEACH_BITBUCKET_CLOUD_PASSWORD", None),
    "daysOpenThreshold": 2,
    "countToDisplay": 5,
    "outputMethod": DEFAULT_OUTPUT_METHOD,
    "sourceControl": DEFAULT_SOURCE_CONTROL,
    # TODO: probably losing boolean value if it comes from env
    "printOnlyActionable": os.environ.get("BLEACH_PRINT_ONLY_ACTIONABLE", False),
}
