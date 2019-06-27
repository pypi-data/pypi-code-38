from orchestrate.core.cement_utils import ArgparseArgumentHandler
from orchestrate.runner.optimizer import SigOptOptimizer
from orchestrate.runner.options import Options


def parse_args():
  parser = ArgparseArgumentHandler()
  parser.add_argument(
    '-c',
    '--command',
    type=str,
    help='The command to run your model.'
  )
  return parser.parse_args()

def main():
  args = parse_args()
  options = Options.from_env()
  optimizer = SigOptOptimizer(
    log_path=options.log_path,
    suggestion_path=options.suggestion_path,
    pod_name=options.pod_name,
    experiment_id=options.experiment_id,
    run_command=args.command if args.command is not None else options.load_config()['run_command'],
  )
  optimizer.optimization_loop()
