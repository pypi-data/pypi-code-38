from ioflow.corpus import Corpus
from ioflow.task_status import TaskStatus
from ioflow.model_saver import ModelSaver
from ioflow.performance_metrics import PerformanceMetrics
from ioflow.configure import read_configure

from seq2label.input import build_input_func
from seq2label.model import Model

raw_config = read_configure()
model = Model(raw_config)

config = model.get_default_config()
config.update(raw_config)

task_status = TaskStatus(config)

# read data according configure
corpus = Corpus(config)
corpus.prepare()
train_data_generator_func = corpus.get_generator_func(corpus.TRAIN)
eval_data_generator_func = corpus.get_generator_func(corpus.EVAL)

corpus_meta_data = corpus.get_meta_info()

# config['vocab_data'] = corpus_meta_data['vocab']
# vocab_data_file = pkg_resources.resource_filename(__name__, '../data/unicode_char_list.txt')
# config['vocab_data'] = np.loadtxt(vocab_data_file, dtype=np.unicode, encoding=None)

# build model according configure


# send START status to monitor system
task_status.send_status(task_status.START)

# train and evaluate model
train_input_func = build_input_func(train_data_generator_func, config)
eval_input_func = build_input_func(eval_data_generator_func, config)

config['tags_data'] = corpus_meta_data['tags']
config['num_classes'] = len(config['tags_data'])

# ***** test ******

import tensorflow as tf
import sys

# data_generator = train_data_generator_func()
# for i, data in enumerate(data_generator):
#     print(i, data)
#
# sys.exit(0)

# train_iterator = train_input_func()
# with tf.Session() as sess:
#     sess.run(tf.tables_initializer())
#
#     counter = 0
#     while True:
#         try:
#             value = sess.run(train_iterator)
#             counter += 1
#             print(value)
#             break
#         except tf.errors.OutOfRangeError:
#             break
#
# print(counter)
# #
# sys.exit(0)
# ***** /test ******

evaluate_result, export_results, final_saved_model = model.train_and_eval_then_save(
    train_input_func,
    eval_input_func,
    config
)

task_status.send_status(task_status.DONE)

# if evaluate_result:
#     performance_metrics = PerformanceMetrics(config)
#     performance_metrics.set_metrics('test_loss', evaluate_result['loss'])
#     performance_metrics.set_metrics('test_acc', evaluate_result['acc'])

model_saver = ModelSaver(config)
model_saver.save_model(final_saved_model)
