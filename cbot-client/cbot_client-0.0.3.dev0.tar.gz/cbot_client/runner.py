import os
import platform
import subprocess
import tempfile

from cbot_client.index_storage import IndexStorage
from cbot_client.profiler import ProfileGetter
from cbot_client.tools import environment_append


def get_docker_image_name(settings):
    docker_image = "conanio/{}{}".format(settings["compiler"],
                                         settings["compiler.version"].replace(".", ""))
    return docker_image


def run_create(index_path, ref, pid=None):

    cur_os = {"Darwin": "Macos"}.get(platform.system(), platform.system())

    storage = IndexStorage(index_path)
    pr = ProfileGetter(pid)

    settings = None
    if pid:
        settings, options = pr.get_profile_settings_options()
        if settings["os_build"] != "Linux" and cur_os != settings["os_build"]:
            raise Exception("Cannot run a build of {} in this system".format(settings["os_build"]))

    tmp_path = tempfile.mkdtemp()
    profile_path = os.path.join(tmp_path, "profile.txt")
    with open(profile_path, "w") as fd:
        fd.write(str(pr))

    recipe_folder = storage.real_recipe_folder(*ref.split("/"))
    print("Running at: {}".format(recipe_folder))
    cmd_template = "conan create . {}@cbot/stable --profile {}"
    my_env = os.environ.copy()

    if (settings and settings["os_build"] == "Linux") or (not settings and cur_os == "Linux"):
        docker_image = get_docker_image_name(settings)
        inside = "pip install conan --upgrade && pip install cbot-client && cbot install_hook && " + \
                 cmd_template.format(ref, "/tmp/profile.txt")
        cmd = 'docker run --rm -v{}:/home/conan -v{}:/tmp ' \
              '-e CONAN_HOOK_ERROR_LEVEL=40 ' \
              '{} /bin/bash -c "{}"'.format(recipe_folder, tmp_path, docker_image, inside)
    else:
        cmd = cmd_template.format(ref, profile_path)
        my_env["CONAN_HOOK_ERROR_LEVEL"] = "40"

    print("---------------------  RUNNING  ---------------------\n{}\n".format(cmd))
    with environment_append(my_env):
        code = os.system(cmd)
        if code != 0:
            raise Exception("The command '{}' failed! ".format(cmd))
