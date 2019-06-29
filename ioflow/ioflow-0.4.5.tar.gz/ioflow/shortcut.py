from ioflow.corpus import Corpus
from ioflow.task_status import TaskStatus
from ioflow.model_saver import ModelSaver
from ioflow.performance_metrics import PerformanceMetrics
from ioflow.configure import read_configure

config = read_configure()

task_status = TaskStatus(config)
# task_status.send_status(task_status.START)


# read data according configure
corpus = Corpus(config)
corpus.prepare()
train_data_generator_func = corpus.get_generator_func(corpus.TRAIN)

corpus_meta_data = corpus.get_meta_info()


performance_metrics = PerformanceMetrics(config)
# performance_metrics.set_metrics('test_loss', evaluate_result['loss'])

model_saver = ModelSaver(config)
# model_saver.save_model(final_saved_model)

__all__ = [
    'config', 'task_status', 'corpus', 'train_data_generator_func',
    'corpus_meta_data', 'performance_metrics', 'model_saver'
]
