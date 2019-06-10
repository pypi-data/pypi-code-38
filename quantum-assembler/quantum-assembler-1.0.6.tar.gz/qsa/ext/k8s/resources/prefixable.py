

class Prefixable:
    """A resource type that allows its namespace to be prefixed
    with a variable. This may then be used to deploy resources
    to different environments.
    """
    pass


class ClusterPrefixable:
    cluster_wide = True
