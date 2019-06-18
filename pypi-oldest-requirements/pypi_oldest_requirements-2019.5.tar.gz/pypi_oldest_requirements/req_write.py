
def write_exact_pinned_requirements(filename, req_version_tuples):
    open(filename, 'wt').writelines((f'{name}=={version}\n' for name, version in req_version_tuples))


def write_requirements(filename, lines):
    open(filename, 'wt').writelines(lines)
