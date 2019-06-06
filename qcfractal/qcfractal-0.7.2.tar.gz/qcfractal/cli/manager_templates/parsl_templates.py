__all__ = ['parsl_dict', 'base_dict']

base_dict = {
    "MANAGER_NAME_SHORT": "Parsl",
    "MANAGER_NAME_LONG": "Parsl Parallel Scripting Library",
    "MANAGER_URL_TITLE": "Parsl",
    "MANAGER_URL": "https://parsl.readthedocs.io/en/latest/index.html",
    "MANAGER_CLIENT": "parsl_config",
    "SANITY_CHECKS": "",
    "IMPORTS": """
from parsl.config import Config
from parsl.executors.ipp import HighThroughputExecutor
""",

    "MANAGER_CLIENT_BUILDER": ""
}

code_skeletal = """
config = Config(
    executors=[
        HighThroughputExecutor(
            label='QCFractal Compute Executor',
            provider={PROVIDER}(
                queue=TORQUE_QUEUE,
                account=TORQUE_ACCOUNT,
                scheduler_options=SCHEDULER_OPTS,
                worker_init=TASK_STARTUP_COMMANDS,
                walltime="00:10:00",
                init_blocks=1,
                max_blocks=MAX_NODES,
                nodes_per_block=1,        # Keep one node per block, its just easier this way
            ),
            workers_per_node=MAX_TASKS_PER_NODE,
        )

    ],
)

"""

# SLURM

slurm_imports = base_dict["IMPORTS"] + "\n" + """"from parsl.providers import TorqueProvider"""

slurm_sanity_checks = """
if NODE_EXCLUSIVITY and "--exclusive" not in SCHEDULER_OPTS:
    SCHEDULER_OPTS.append("--exclusive")
"""

slurm_builder = """
cluster = SLURMCluster(
    name='QCFractal Dask Compute Executor',
    cores=CORES_PER_NODE,
    memory=str(MEMORY_PER_NODE) + "GB",
    queue=SLURM_PARTITION,
    processes=MAX_TASKS_PER_NODE,  # This subdivides the cores by the number of processes we expect to run
    walltime="00:10:00",

    # Additional queue submission flags to set
    job_extra=SCHEDULER_OPTS,
    # Not sure of the validity of this, but it seems to be the only terminal-invoking way
    # so python envs may be setup from there
    # Commands to execute before the Dask
    env_extra=TASK_STARTUP_COMMANDS
)
"""

# PBS/Torque

torque_imports = base_dict["IMPORTS"] + "\n" + """"from dask_jobqueue import PBSCluster"""

torque_builder = """
cluster = PBSCluster(
    name='QCFractal Dask Compute Executor',
    cores=CORES_PER_NODE,
    memory=str(MEMORY_PER_NODE) + "GB",
    queue=TORQUE_QUEUE,
    project=TORQUE_ACCOUNT,
    processes=MAX_TASKS_PER_NODE,  # This subdivides the cores by the number of processes we expect to run
    walltime="00:10:00",

    # Additional queue submission flags to set
    job_extra=SCHEDULER_OPTS,
    # Not sure of the validity of this, but it seems to be the only terminal-invoking way
    # so python envs may be setup from there
    # Commands to execute before the Dask
    env_extra=TASK_STARTUP_COMMANDS
)
"""

# LSF

lsf_imports = base_dict["IMPORTS"] + "\n" + """"from dask_jobqueue import LSFCluster"""

lsf_builder = """
cluster = LSFCluster(
    name='QCFractal Dask Compute Executor',
    cores=CORES_PER_NODE,
    memory=str(MEMORY_PER_NODE) + "GB",
    queue=LSF_QUEUE,
    project=LSF_PROJECT,
    processes=MAX_TASKS_PER_NODE,  # This subdivides the cores by the number of processes we expect to run
    walltime="00:10:00",

    # Additional queue submission flags to set
    job_extra=SCHEDULER_OPTS,
    # Not sure of the validity of this, but it seems to be the only terminal-invoking way
    # so python envs may be setup from there
    # Commands to execute before the Dask
    env_extra=TASK_STARTUP_COMMANDS
)
"""


# Final

parsl_dict = {
    "slurm": {**base_dict,
              **{"SANITY_CHECKS": slurm_sanity_checks,
                 "IMPORTS": slurm_imports,
                 "MANAGER_CLIENT_BUILDER": code_skeletal.format(BUILDER=slurm_builder),
                 }
              },
    "torque": {**base_dict,
               **{"IMPORTS": torque_imports,
                  "MANAGER_CLIENT_BUILDER": code_skeletal.format(BUILDER=torque_builder)}
               },
    "lsf": {**base_dict,
            **{"IMPORTS": lsf_imports,
               "MANAGER_CLIENT_BUILDER": code_skeletal.format(BUILDER=lsf_builder)}
            }
}
