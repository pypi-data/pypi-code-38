def read_conda_env_contents(conda_file_name):
    if not conda_file_name:
        return None
    with open(conda_file_name) as conda_f:
        return conda_f.read()
