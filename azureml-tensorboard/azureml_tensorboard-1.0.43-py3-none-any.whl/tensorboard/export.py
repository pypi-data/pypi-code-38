# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines utilities to export Run History data to a tensorboard logs directory."""
import os
import logging
from azureml._restclient.experiment_client import ExperimentClient
try:
    import tensorflow as tf
except ImportError:
    print("Could not import tensorflow, required for tensorboard")

module_logger = logging.getLogger(__name__)


def _write_scalar_summary(summary_writer, tag, value, step):
    summary = tf.Summary()
    summary.value.add(tag=tag, simple_value=value)
    summary_writer.add_summary(summary, step)


def export_to_tensorboard(run_data, logsdir, logger=None, recursive=True):
    """Export a run or a list of runs to a tensorboard logs directory.

    Parameters:
        run_data : azureml.core.Run or a list of Run objects
            A run or a list of runs to export.

        logsdir : str
            The path to the logs directory to export to.

        logger : logging
            Optional user-specified logger to log to.

        recursive: bool
            Specifies whether to recursively retrieve all child runs for specified runs.

    """
    _logger = logger if logger else module_logger
    if isinstance(run_data, (list,)):
        if not run_data:
            raise Exception("export failed: run_data cannot be empty list")
        runs = run_data
        experiment = run_data[0].experiment
    else:
        try:
            from azureml.core import Run
            # If this is a experiment get all runs
            runs = Run.list(run_data.workspace, run_data.name)
            experiment = run_data
        except AttributeError:
            # Otherwise, this is a run
            runs = [run_data]
            # Note: we assume this method is always scoped to a single project, as discussed with AK
            experiment = run_data.experiment
    if recursive:
        runs += [child for run in runs for child in run.get_children(recursive=True)]
    client = ExperimentClient(experiment.workspace.service_context, experiment.name)

    run_ids = [run.id for run in runs]
    all_metrics = client.get_metrics_by_run_ids(run_ids)
    run_id = None
    writer = None
    for run_metrics in all_metrics:
        old_run_id = run_id
        run_id = run_metrics.run_id
        if old_run_id != run_id:
            if writer is not None:
                writer.close()
            # Create new file writer for each new runid
            writer = tf.summary.FileWriter(os.path.join(logsdir, run_id))
        metrics = run_metrics.cells
        step = 0
        for cell in metrics:
            for key, value in cell.items():
                if type(value) == str:
                    _logger.debug(type(value))
                else:
                    _write_scalar_summary(writer, key, value, step)
                    step = step + 1
    if writer is not None:
        writer.close()
