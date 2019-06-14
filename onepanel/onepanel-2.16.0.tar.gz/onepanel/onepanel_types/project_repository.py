import click
from onepanel.models.project_repository import ProjectRepository

class ProjectRepositoryParamType(click.ParamType):
    name = 'project_repository'

    def convert(self, value, param, ctx):
        """Accepts """
        try:
            project_repository = ProjectRepository()
            key_values = value.split(',')

            for kv in key_values:
                parts = kv.split('=')
                setattr(project_repository, parts[0], parts[1])
            
            return project_repository
        except ValueError:
            self.fail('%s is not valid' % value, param, ctx)

PROJECT_REPOSITORY = ProjectRepositoryParamType()