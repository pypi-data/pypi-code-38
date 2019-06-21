import os
from pkg_resources import iter_entry_points

from invoke import Collection

from .utils.env_template import ENV_TEMPLATE

if not os.getenv("CS_LOADER_ACTIVE"):
    from io import StringIO
    from dotenv import load_dotenv
    load_dotenv(stream=StringIO(ENV_TEMPLATE))

LOADER_DIST_ENABLED = bool(int(os.environ["CS_LOADER_DIST_ENABLED"]))
TASK_ENTRY_POINTS_GROUP = os.environ["CS_TASK_ENTRY_POINTS_GROUP"]


def build_tasks_namespace():
    """Build a namespace with tasks from included CivilServant libraries."""
    ns = Collection()
    for entry_point in iter_entry_points(TASK_ENTRY_POINTS_GROUP):
        name = entry_point.name.lower()
        if entry_point.name in ("env", "core"):
            # Promote env tasks and core tasks into the root namespace
            entry_point_col = Collection.from_module(entry_point.load())
            for task in entry_point_col.tasks.values():
                ns.add_task(task)
            for col in entry_point_col.collections.values():
                ns.add_collection(col)
        elif entry_point.name != "dist" or LOADER_DIST_ENABLED:
            # Add the collection into its own child namespace
            ns.add_collection(entry_point.load())
    return ns

namespace = build_tasks_namespace()

