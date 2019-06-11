import gitlab
import os


def get_pipe_max(envs):
    """
    Get the max number of pipelines for each ref/branch
    :param envs:
    :return:
    """
    return int(envs.get("GITLAB_MAX_BRANCH_PIPELINES", 2))


def get_token(envs):
    """
    Get the API token from the environment
    :param envs:
    :return:
    """
    return envs.get("GITLAB_API_TOKEN")


def get_server(envs):
    """
    Get the server address
    :param envs:
    :return:
    """
    apiurl = envs.get("CI_API_V4_URL")

    proto, address = apiurl.split("://", 1)
    host, _ = address.split("/", 1)
    server = "{}://{}".format(proto, host)
    return server


def get_project_pipelines(envs):
    """
    Get all running pipelines for this project
    :param envs:
    :return:
    """
    token = get_token(envs)
    server = get_server(envs)
    api = gitlab.Gitlab(server, private_token=token)
    project = api.projects.get(envs.get("CI_PROJECT_ID"))

    pipelines = project.pipelines.list(page=1, per_page=50)

    running = [x for x in pipelines if x.status == "running"]

    return running


def abort_old_pipelines(envs):
    """
    Abort the older running pipelines for this branch
    :param envs:
    :return:
    """
    running = get_project_pipelines(envs)
    branch = [x for x in running if x.ref == envs.get("CI_COMMIT_REF_NAME")]

    limit = get_pipe_max(envs)

    print("Configured for a limit of {} per ref".format(limit))

    # oldest first
    byage = sorted(branch, key=lambda x: int(x.id), reverse=False)

    print("There are {} pipelines running for this ref".format(len(byage)))

    # the limit number oldest running pipelines on this reference
    tokill = byage[:-limit]

    if len(tokill):
        print("Killing old pipelines")
        for pipe in tokill:
            print("Cancel old pipeline {}".format(pipe.id))
            pipe.cancel()
    else:
        print("No action required")
