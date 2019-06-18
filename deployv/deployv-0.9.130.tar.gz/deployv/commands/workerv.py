# coding: utf-8

import click
import signal
from deployv.base import errors
from deployv.helpers import utils, configuration_helper


def signal_handler(signal_number, stack_frame):
    raise errors.GracefulExit(
        'Received a signal to terminate, stopping workers'
    )


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@click.command()
@click.option("-l", "--log_level", help="Log level to show", default='INFO')
@click.option("-h", "--log_file", help="Write log history to a file")
@click.option("-C", "--config", help="Additional .conf files.")
@click.option(
    "--status-worker", is_flag=True,
    help=("Parameter used to specify a worker as a status worker."
          " Status workers only answer the ping messages sent to know the"
          " status of the server")
)
def run(log_level, log_file, config, status_worker):
    utils.setup_deployv_logger(level=log_level, log_file=log_file)
    cfg = configuration_helper.DeployvConfig(worker_config=config)
    worker_type = cfg.deployer.get('worker_type')
    module = __import__('deployv.messaging', fromlist=[str(worker_type)])
    if not hasattr(module, worker_type):
        raise ValueError
    msg_object = getattr(module, worker_type)
    config_class = msg_object.CONFIG_CLASSES['file']
    name = 'Deploy worker' if not status_worker else 'Status worker'
    worker = msg_object.factory(
        config_class(cfg, status=status_worker), name
    )
    try:
        worker.run()
    except (KeyboardInterrupt, errors.GracefulExit):
        worker.signal_exit()
