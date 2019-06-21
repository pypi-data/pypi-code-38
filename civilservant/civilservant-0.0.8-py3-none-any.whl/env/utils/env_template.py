import os
import tempfile
from pathlib import Path

"""
This is a temporary file with a constant that's identical to the contents of
the CivilServant Loader's .env.template. This is here as a temporary
workaround until I figure out why the .env.template file isn't being stored in
the python egg despite being listed in the correct sections of config.cfg from
what I can see. This will be removed once the issue is resolved.
"""

ENV_TEMPLATE = """
# Loader Configuration
# (You shouldn't need to edit this section)
export CS_CORE_LIB_URL="git+https://github.com/mitmedialab/civilservantlib#egg=civilservant-core"
export CS_LOADER_ACTIVE=1
export CS_LOADER_DIST_ENABLED=0
export CS_PACKAGE_DIR_PREFIX="civilservantlib-"
export CS_PACKAGE_PREFIX="civilservant-"
export CS_PACKAGE_URL_PREFIX="git+https://github.com/mitmedialab/"
export CS_PROJECT_LIBS_PATH="lib"
export CS_TASK_ENTRY_POINTS_GROUP="civilservant_tasks"

"""

def _get_temp_root_env():
    """Create a temporary file containing the .env.template above."""
    filename = next(tempfile._get_candidate_names())
    temp_path = Path(tempfile.gettempdir(), filename)
    with open(str(temp_path), "w") as f:
        f.write(ENV_TEMPLATE)
    return Path(temp_path)

