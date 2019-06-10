import subprocess


def git_revision_hash():
    """
    获取当前 commit id
    """
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip().replace(r"\n", "")
    except Exception:
        return "Not found"
