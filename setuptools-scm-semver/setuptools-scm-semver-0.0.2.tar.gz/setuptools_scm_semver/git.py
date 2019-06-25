from setuptools_scm import Configuration
from setuptools_scm import meta
from setuptools_scm.git import _git_parse_describe
from setuptools_scm.git import DEFAULT_DESCRIBE
from setuptools_scm.git import GitWorkdir
from setuptools_scm.git import warn_on_shallow
from setuptools_scm.utils import has_command


def parse(
    root, describe_command=DEFAULT_DESCRIBE, pre_parse=warn_on_shallow, config=None
):
    """
    :param pre_parse: experimental pre_parse action, may change at any time
    """
    if not config:
        config = Configuration(root=root)

    if not has_command("git"):
        return

    wd = GitWorkdir.from_potential_worktree(config.absolute_root)
    if wd is None:
        return
    if pre_parse:
        pre_parse(wd)

    if config.git_describe_command:
        describe_command = config.git_describe_command

    out, unused_err, ret = wd.do_ex(describe_command)
    if ret:
        # If 'git git_describe_command' failed, try to get the information otherwise.
        branch, err, ret = wd.do_ex("git symbolic-ref --short HEAD")

        rev_node = wd.node()
        dirty = wd.is_dirty()

        if rev_node is None:
            return meta("0.0", distance=0, dirty=dirty, branch=branch, config=config)

        return meta(
            "0.0",
            distance=wd.count_all_nodes(),
            node="g" + rev_node,
            dirty=dirty,
            branch=wd.get_branch(),
            config=config,
        )
    else:
        tag, number, node, dirty = _git_parse_describe(out)

        branch = wd.get_branch()
        if number:
            return meta(
                tag,
                config=config,
                distance=number,
                node=node,
                dirty=dirty,
                branch=branch,
            )
        else:
            return meta(tag, config=config, node=node, dirty=dirty, branch=branch)
