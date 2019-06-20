import getpass
import os

from libsubmit.providers import SlurmProvider
from libsubmit.channels import LocalChannel
from libsubmit.launchers import SrunLauncher

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

USERNAME = getpass.getuser()
SCRIPT_DIR = os.environ.get("CECI_SCRIPT_DIR", 
            os.path.join(os.environ["SCRATCH"], "parsl-scripts"))  # default value


CORI_OVERRIDE="""#SBATCH --constraint=haswell                                        
module load python/3.5-anaconda ; source activate parsl_env_3.5
"""

def make_config(nodes=1, walltime_minutes=20, queue='debug'):
    label=f'cori_{nodes}_{walltime_minutes}'
    config = Config(
        executors=[
            IPyParallelExecutor(
                label=label,
                provider=SlurmProvider(
                    queue,
                    channel=LocalChannel(script_dir=SCRIPT_DIR),
                    walltime=f"00:{walltime_minutes}:00"
                    nodes_per_block=nodes,
                    tasks_per_node=1,
                    init_blocks=1,
                    max_blocks=1,
                    overrides=CORI_OVERRIDE,
                    launcher=SrunLauncher,
                ),
                controller=Controller(),
            )
        ],
        run_dir="./ceci-runs",
    )