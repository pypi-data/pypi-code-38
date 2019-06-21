from dataclasses import dataclass
from typing import List

@dataclass
class MLFlowConfig:
    cluster_tracker_uri: str ="http://mlflow.default.svc.cluster.local:5000"
    tracker_uri: str ="http://localhost"
    tracker_port: int = 5000

    @property
    def tracking_uri(self):
        return f'{self.tracking_uri}:{self.tracker_port}'



class MLFlowLogger():
    name = 'mlflow'

    def __init__(self, project_name, experiment_name, C: MLFlowConfig):
        import mlflow
        self.mlflow = mlflow
        self.mlflow.set_tracking_uri(C.tracking_uri)
        self.mlflow.set_experiment(experiment_name)
        self.project_name = project_name

    def start_expt(expt_id=None): self.mlflow.start_run(expt_id)
    def end_expt(): self.mlflow.end_run()

    #log any scalar value
    def log_scalar(self, name, value, step):
        self.mlflow.log_metric(name, value)

    #log hyper-parameter
    def log_hp(self, key, value):
        self.mlflow.log_param(key, value)

    def log_artifacts(self, from_dir, artifact_path):
        self.mlflow.log_artifacts(from_dir, artifact_path=artifact_path)



@dataclass
class PytorchTBConfig:
    output_dir: str = './logs'

class PytorchTensorBoardLogger():
    name = 'tensorboard.pt'

    def __init__(self, project_name, experiment_name, C: PytorchTBConfig):
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(C.output_dir)
        self.project_name = project_name
        self.experiment_name = experiment_name

    def start_expt(expt_id=None): pass
    def end_expt(): pass

    def log_scalar(self, name, value, step):
        self.writer.add_scalar(name, value, step)

    def log_hp(self, key, value):
        self.log_scalar(key, value, 0)

    def log_histogram(self, name, value, step):
        self.writer.add_histogram(name, value, step)



@dataclass
class MultiLoggerConfig:
    project_name: str = ''
    experiment_name: str
    mlflow: MLFlowConfig = None
    tb: PytorchTBConfig = None



class MultiLogger():
    name = 'multilogger'
    known_loggers = ['mlflow', 'tensorboard.pt']

    def __init__(self, C: MultiLoggerConfig, loggers: List[str]):
        self.loggers = loggers
        self.experiment_name = C.experiment_name
        self.name2logger = {}
        
        for l in loggers:
            if l == 'mlflow':
                self.name2logger[l] = MLFlowLogger(C.project_name, C.experiment_name, C.mlflow)
            elif l == 'tensorboard.pt':
                self.name2logger[l] = PytorchTensorBoardLogger(C.project_name, C.experiment_name, C.tb)

            else:
                raise Exception(f'Unsupported logger name: {l}, Supported: {known_loggers}')

    def start_expt(expt_id=None):
        for l, logger in self.name2logger.items(): logger.start_expt(expt_id=expt_id)
    def end_expt():
        for l, logger in self.name2logger.items(): logger.end_expt()

    def get_logger_by_name(self, logger):
        return self.name2logger[logger]

    def log(self, logger: str, dtype: str, **args):
        logger = self.get_logger_by_name (logger)
        if dtype == 'scalar':
            logger.log_scalar(key=args.key, value=args.value, step=args.step)
        elif dtype == 'hp':
            logger.log_hp(key=args.key, value=args.value)
        elif dtype == 'scalardict':
            for k, v in args.value.items():
                logger.log_scalar(key=k, value=v)
        elif dtype == 'hpdict':
            for k, v in args.value.items():
                logger.log_hp(key=k, value=v)
        else:
            raise NotImplementedError



































