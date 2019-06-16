import os
import gitlab
import lazy_import


GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", False)
GITLAB_API_BASE_URL = GITLAB_URL + "/api/v4/"
GITLAB_AUTH_HEADER = {"Private-Token": GITLAB_TOKEN}

PROJECTS = {
    "python": {
        "types": {
            "cli": lazy_import.lazy_callable("glb.utils.new_cli_project"),
            "package": "package",
            "django": "django",
            "django-app": "django-app",
        }
    }
}
ADD_NEW_FN = lazy_import.lazy_callable("glb.utils.add_new_project")

ADD_METHOD = {"new": ADD_NEW_FN, "existing": "existing project"}


gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
