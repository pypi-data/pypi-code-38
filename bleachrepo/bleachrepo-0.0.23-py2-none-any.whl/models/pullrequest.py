class PullRequest(object):
    def __init__(self, repo, createdAt, user, title, url=None):
        self.repo = repo
        self.createdAt = createdAt
        self.user = user
        self.title = title
        self.url = url
