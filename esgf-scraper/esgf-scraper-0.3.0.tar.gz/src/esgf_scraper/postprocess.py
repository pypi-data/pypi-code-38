""" Perform any postprocessing steps required

The configuration which drives the postprocessing is under the `postprocess` heading. More than one processing steps can be
specified. If that is the case the steps are performed in the order specified.

See the example configuration file for example of a simple postprocessing workflow.
"""
from logging import getLogger
from os.path import join, sep
from subprocess import PIPE, CalledProcessError, run

from esgf_scraper import conf

logger = getLogger(__name__)


def run_script(step, item):
    extra_args = {
        "output_dir": join(conf["base_dir"], sep.join(item["instance_id"].split(".")))
    }
    filled_cmd = step["script"].format(**dict(item), **extra_args)
    c = filled_cmd.split()

    # This raises a CalledProcessError if the call fails
    run(c, stdout=PIPE, check=True)


def run_postprocessing(item):
    steps = conf.get("postprocess", [])
    logger.info("processing item: {}".format(item["instance_id"]))
    for step in steps:
        if "name" in step:
            logger.info("Starting step: {}".format(step["name"]))

        try:
            run_script(step, item)
        except (FileNotFoundError, CalledProcessError) as e:
            step_name = step["name"] if "name" in step else "no_name"
            logger.exception(
                "postprocessing step `{}: {}` failed. Dumping output to log".format(
                    step_name, step["script"]
                )
            )
            logger.error(e.stdout)

            # We then want to reraise the error - no further postprocessing is attempted
            raise
