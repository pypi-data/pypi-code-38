"""Functions calling GitLab API."""


def build_schema_url(repo_url, ref, schema_filename):
    return '{}/raw/{}/{}'.format(repo_url.rstrip('/'), ref, schema_filename)


def iter_refs(gl, project_path):
    """Yield tuples of tags and branches defined in the given repository.

    e.g. [('tag', 'v0.0.1'), ('branch', 'master'), ('tag', 'v2.0.0')]
    """
    project = gl.projects.get(project_path)
    for tag in project.tags.list():
        yield ('tag', tag.name)
    for branch in project.branches.list():
        yield ('branch', branch.name)
