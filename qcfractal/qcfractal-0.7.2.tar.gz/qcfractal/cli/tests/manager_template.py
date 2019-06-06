"""
Parsl Manager Helper

Conditions:
- Parsl Parallel Scripting Library
- Manager running on the head node
- SLURM manager

For additional information about the Parsl, please visit this site:
https://parsl.readthedocs.io/en/latest/index.html
"""

# Fractal Settings
# Location of the Fractal Server you are connecting to
FRACTAL_URI = "localhost:7777"

# Queue Manager Settings
# Set whether or not we are just testing the Queue Manger (no Fractal Client needed)
TEST_RUN = False


# How many cores per node you want your jobs to have access to
CORES_PER_NODE = 1
# How much memory per node (in GB) you want your jobs to have access to
MEMORY_PER_NODE = 1
# How many tasks per node you want to execute on
MAX_TASKS_PER_NODE = 1
# Maximum number of nodes to try and consume
MAX_NODES = 1
# Whether or not to claim nodes for exclusive use. We recommend you do, but that's up to you
NODE_EXCLUSIVITY = True

# Generic Cluster Settings
# ========================
# Additional commands to send to the command line (often used as "#SBATCH ..." or '#PBS' headers.)
# This is a per-node type setting, not task. Don't set memory or cpu or wall clock through this
# -- Note ---
# Different Managers interpret this slightly differently, but that should not be your concern, just treat
# each item as though it were a CLI entry and the manager block will interpret
# ------------ 
SCHEDULER_OPTS = []

# Additional commands to start each task with. E.g. Activating a conda environment
# Put each command as its own item in strings
TASK_STARTUP_COMMANDS = []

# SLURM Specific Settings
# Name of the SLURM partition to draw from
SLURM_PARTITION = ''


###################

# QCFractal import
import qcfractal
import qcfractal.interface as portal

# Make sure logging is setup correctly
import tornado.log
tornado.log.enable_pretty_logging()

from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import SlurmProvider

# Quick sanity checks

if CORES_PER_NODE < 1 or not isinstance(CORES_PER_NODE, int):
    raise ValueError("CORES_PER_NODE must be an integer of at least 1")
if MAX_TASKS_PER_NODE < 1 or not isinstance(MAX_TASKS_PER_NODE, int):
    raise ValueError("MAX_TASKS_PER_NODE must be an integer of at least 1")
if MAX_NODES < 1 or not isinstance(MAX_NODES, int):
    raise ValueError("MAX_NODES must be an integer of at least 1")
if MEMORY_PER_NODE <= 0:
    raise ValueError("MEMORY_PER_NODE must be a number > 0")


parsl_config = Config(
    executors=[
        HighThroughputExecutor(
            label='QCFractal_Compute_Executor',
            provider=SlurmProvider(
                SLURM_PARTITION,
                exclusive=NODE_EXCLUSIVITY,
                scheduler_options='#SBATCH ' + '\n#SBATCH '.join(SCHEDULER_OPTS) + '\n',
                worker_init='\n'.join(TASK_STARTUP_COMMANDS),
                walltime="00:10:00",
                init_blocks=1,
                max_blocks=MAX_NODES,
                nodes_per_block=1,        # Keep one node per block, its just easier this way
            ),
            # workers_per_node=MAX_TASKS_PER_NODE,
            cores_per_worker=CORES_PER_NODE // MAX_TASKS_PER_NODE,
            max_workers = MAX_NODES*MAX_TASKS_PER_NODE
        )

    ],
)

# Build a interface to the server
# If testing, there is no need to point to a Fractal Client and None is passed in
# In production, the client is needed
if TEST_RUN:
    fractal_client = None
else:
    fractal_client = portal.FractalClient(FRACTAL_URI, verify=False)
    


# Build a manager
manager = qcfractal.queue.QueueManager(fractal_client, parsl_config, update_frequency=0.5,
                                       cores_per_task=CORES_PER_NODE // MAX_TASKS_PER_NODE,
                                       memory_per_task=MEMORY_PER_NODE // MAX_TASKS_PER_NODE)

# Important for a calm shutdown
from qcfractal.cli.cli_utils import install_signal_handlers
install_signal_handlers(manager.loop, manager.stop)

# Start or test the loop. Swap with the .test() and .start() method respectively
if TEST_RUN:
    manager.test()
else:
    manager.start()
