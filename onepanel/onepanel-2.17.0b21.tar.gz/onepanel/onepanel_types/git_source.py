import click
from onepanel.models.git_source import GitSource

class GitSourceParamType(click.ParamType):
    name = 'git source'

    def convert(self, value, param, ctx):
        """Accepts branch_name/commit=commit_hash"""
        try:
            return GitSource.from_string(value)
        except ValueError:
            self.fail('%s is not a valid git source' % value, param, ctx)

GIT_SOURCE = GitSourceParamType()