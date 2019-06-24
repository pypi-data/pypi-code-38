"""
Call gitlab-emulator's code to execute a job
"""
import glob
import os
import shutil
import tempfile
import subprocess
import time
import stat

import requests
import zipfile

from .common import gethostname, iswindows
from .trace import TraceProxy
from .consts import NAME, VERSION


def get_variable(job, name, default=None):
    """
    Get a named variable from a job
    :param job:
    :param name:
    :param default:
    :return:
    """
    for var in job["variables"]:
        if var["key"] == name:
            return var["value"]
    return default


def archive(trace, config, jobname, tempdir, build_folder, success):
    """
    Create a zip archive of the build artifacts if required
    :param trace: trace proxy
    :param config: global gitlab config data
    :param jobname: the job name
    :param tempdir: the temporary data folder
    :param build_folder: the root folder of this build
    :param success: True for successful builds
    :return:
    """
    # handle artifact upload
    job_config = config[jobname]
    if "artifacts" in job_config:
        when = "on_success"  # default
        if "when" in job_config["artifacts"]:
            when = job_config["artifacts"]["when"]

        if when != "always":
            if when == "on_success" and not success:
                return None
            if when == "on_failure" and success:
                return None

        trace.writeline("\nFinding artifacts...")

        paths = job_config["artifacts"]["paths"]
        zipname = "archive.zip"
        if "name" in job_config["artifacts"]:
            # TODO expand variables for this
            zipname = job_config["artifacts"]["name"] + ".zip"

        zippath = os.path.join(tempdir, zipname)
        with zipfile.ZipFile(zippath, "w") as zipobj:
            for item in paths:
                trace.writeline(".. finding {}".format(item))
                # patterns are posix paths and globs, convert them to local
                localpatt = os.path.join(build_folder, item)
                matches = glob.glob(localpatt)
                for include in matches:
                    relpath = os.path.relpath(include, build_folder)
                    if os.path.isfile(include):
                        trace.writeline(".. match {}".format(include))
                        zipobj.write(include, relpath)
                    if os.path.isdir(include):
                        # recurse adding the whole folder
                        for root, _, files in os.walk(include):
                            for file in files:
                                fname = os.path.join(root, file)
                                relname = os.path.relpath(fname, build_folder)
                                trace.writeline(".. match {}".format(relname))
                                zipobj.write(fname, relname)
        return zippath
    return None


def clean(trace, folder, docker, attempts=10):
    """
    Totally delete the given folder regardless of permissions inside
    :param trace:
    :param folder:
    :param docker:
    :param attempts: retry this many times
    :return:
    """
    from gitlabemu import logmsg

    logmsg.info("Cleaning build {}".format(folder))
    # make everything deletable on windows
    if iswindows():
        for root, dirs, files in os.walk(folder):
            for item in files + dirs:
                path = os.path.join(root, item)
                if not os.access(path, os.W_OK):
                    # shutil.rmtree() will barf on ro files
                    os.chmod(path, stat.S_IWUSR)
                    # so lets delete it now
                    os.unlink(path)
    try:
        try:
            shutil.rmtree(folder)
        except:
            # failed, if we have docker, try to use that
            if docker:
                from gitlabemu import logmsg
                if iswindows():
                    logmsg.fatal("unable to clean {}".format(folder))
                else:
                    # try to use a busybox
                    parent = os.path.abspath(os.path.dirname(folder))
                    foldername = os.path.basename(folder)
                    subprocess.check_call(
                        ["docker", "run", "--rm",
                         "-w", parent,
                         "-v", parent + ":" + parent,
                         "busybox:latest",
                         "rm", "-rf", foldername
                         ])
                    return
            raise
    except Exception as err:
        # possibly this is windows virus scanning?
        if attempts > 0:
            trace.writeline("clean failed.. sleeping ".format(err, attempts))
            time.sleep(3 * (4 - attempts))
            clean(trace, folder, docker, attempts - 1)
        else:
            trace.writeline("Error cleaning after build {}".format(err))
            raise


def run(runner, job, docker):
    """
    Execute the given job here using gitlab-emulator
    :param runner: the runner object
    :param job: the job response from the server
    :param docker: if True, we can use docker for housekeeping
    :return:
    """
    from gitlabemu import configloader
    from gitlabemu import logmsg
    from gitlabemu import errors

    trace = TraceProxy(runner, job)

    logmsg.FATAL_EXIT = False

    trace.writeline("Running on {} {} {}".format(gethostname(), NAME, VERSION))
    if docker:
        trace.writeline("Using Docker executor")
    else:
        trace.writeline("Using shell executor")

    tempdir = tempfile.mkdtemp(dir=runner.builds)
    build_dir = os.path.join(tempdir, get_variable(job, "CI_PROJECT_PATH"))
    build_dir_abs = os.path.abspath(build_dir)
    try:
        os.makedirs(build_dir)

        # clone the git repo defined in the job
        git = job["git_info"]

        trace.writeline("Cloning project..")
        trace.write(subprocess.check_output([
            "git", "clone", git["repo_url"], build_dir
        ], cwd=tempdir, stderr=subprocess.STDOUT))

        # checkout the ref to build
        trace.write(subprocess.check_output([
            "git", "checkout", "-f", get_variable(job, "CI_BUILD_REF")
        ], cwd=build_dir_abs, stderr=subprocess.STDOUT))

        # load the config
        ci_file = os.path.join(build_dir_abs,  get_variable(job, "CI_CONFIG_PATH"))
        config = configloader.read(ci_file)

        # populate real vars
        for var in job["variables"]:
            name = var["key"]
            config["variables"][name] = var["value"]

        jobname = job["job_info"]["name"]
        emulator_job = configloader.load_job(config, jobname)
        trace.emulator_job = emulator_job

        runner.get_dependencies(trace, job, build_dir_abs)

        emulator_job.stdout = trace

        success = False
        error = False

        try:
            emulator_job.run()
            success = True
        except errors.GitlabEmulatorError:
            # the job failed
            emulator_job.abort()
        except requests.HTTPError:
            error = True
            emulator_job.abort()

        if not error:  # success or failure but not some internal errors
            archive_file = archive(trace, config, jobname, tempdir, build_dir_abs, success)
            if archive_file:
                runner.upload(trace, job, archive_file)

        trace.writeline("Job complete success={}".format(success))
        return success
    finally:
        clean(trace, tempdir, docker)
