def make_collection_name(git_repo, git_repo_dir, kitchen_name):
    """
    Generate the name of a mongodb collection from git and kitchen details.

    :param git_repo: Git repository name
    :param git_repo_dir: Git repository directory name
    :param kitchen_name: Kitchen name
    :return:
    """
    return '{}{}{}'.format(git_repo, git_repo_dir, kitchen_name)
