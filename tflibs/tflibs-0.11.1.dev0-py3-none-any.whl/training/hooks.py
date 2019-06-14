"""
    Session Run Hooks
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import threading
import os
import collections
from shutil import copy

import tensorflow as tf
from tflibs.image import encode


class BestModelExporterArgs(collections.namedtuple('BestModelExporterArgs',
                                                   ['serving_input_receiver_fn', 'metric_name', 'save_max'])):
    def __new__(cls, serving_input_receiver_fn, metric_name, save_max=True):
        return super(BestModelExporterArgs, cls).__new__(cls, serving_input_receiver_fn, metric_name, save_max)

    @property
    def __dict__(self):
        return super(BestModelExporterArgs, self)._asdict()


class EvaluationRunHook(tf.train.SessionRunHook):
    def __init__(self, estimator: tf.estimator.Estimator, input_fn, eval_steps: int, summary=True,
                 best_model_exporter_args: BestModelExporterArgs = None):
        self._estimator = estimator
        self._input_fn = input_fn
        self._eval_steps = eval_steps
        self._summary = summary
        self._lock = threading.Lock()
        self._eval_dir = os.path.join(self.estimator.model_dir, 'eval')
        self._best_model_exporter_args = best_model_exporter_args
        self._best_model_exporter = None  # type: BestModelExporter

    @property
    def estimator(self):
        return self._estimator

    @property
    def input_fn(self):
        return self._input_fn

    @property
    def eval_steps(self):
        return self._eval_steps

    @property
    def summary(self):
        return self._summary

    @property
    def lock(self):
        return self._lock

    @property
    def best_model_exporter_args(self):
        return self._best_model_exporter_args

    @property
    def best_model_exporter(self):
        return self._best_model_exporter

    @property
    def eval_dir(self):
        return self._eval_dir

    def begin(self):
        if self._best_model_exporter_args is not None:
            self._best_model_exporter = BestModelExporter(estimator=self.estimator,
                                                          **vars(self.best_model_exporter_args))

    def before_run(self, run_context: tf.train.SessionRunContext):
        return tf.train.SessionRunArgs({'global_step': tf.train.get_or_create_global_step()})

    def after_run(self,
                  run_context: tf.train.SessionRunContext,  # pylint: disable=unused-argument
                  run_values: tf.train.SessionRunValues):
        global_step = run_values.results['global_step']
        if (global_step + 1) % self.eval_steps == 0:
            # Start new thread for evaluation
            t = threading.Thread(target=self._run_evaluation, args=(run_context,))
            t.start()
            t.join()

    def _run_evaluation(self, run_context: tf.train.SessionRunContext):
        if self.lock.acquire(False):
            hooks = []

            if self.summary:
                hooks.append(EvalSummaryHook(self.eval_dir))

            try:
                metrics = self.estimator.evaluate(self.input_fn, hooks=hooks)

                if self.best_model_exporter is not None:
                    self.best_model_exporter.check_n_update(metrics)

            except Exception as e:
                tf.logging.info('Evaluation went wrong...')
                run_context.request_stop()
                raise e
            finally:
                self.lock.release()


class EvalSummaryHook(tf.train.SessionRunHook):
    def __init__(self,
                 summary_dir: str,
                 summary_op=None):
        self._summary_dir = summary_dir
        self._summary_op = summary_op
        self._summary_writer = None  # type: tf.summary.FileWriter
        self._finished = False

    def begin(self):
        self._summary_op = self._summary_op or tf.summary.merge_all()
        self._summary_writer = tf.summary.FileWriterCache.get(self._summary_dir)  # type: tf.summary.FileWriter

    def before_run(self, run_context: tf.train.SessionRunContext):
        return tf.train.SessionRunArgs({
            'summary': self._summary_op,
            'global_step': tf.train.get_or_create_global_step()
        }) if not self._finished and self._summary_op is not None else None

    def after_run(self,
                  run_context: tf.train.SessionRunContext,  # pylint: disable=unused-argument
                  run_values: tf.train.SessionRunValues):
        if not self._finished:
            self._summary_writer.add_summary(run_values.results['summary'], run_values.results['global_step'])
            self._finished = True


class BestModelExporter:
    def __init__(self, estimator: tf.estimator.Estimator, serving_input_receiver_fn, metric_name: str, save_max=True):
        self._estimator = estimator
        self._serving_input_receiver_fn = serving_input_receiver_fn

        self._metric_name = metric_name
        self._save_max = save_max
        eval_dir = os.path.join(self.estimator.model_dir, 'eval')
        os.makedirs(eval_dir, exist_ok=True)
        self._ckpt_path = os.path.join(eval_dir, 'best-metric')

        self._build_graph()
        self._restore()

    @property
    def estimator(self):
        return self._estimator

    @property
    def serving_input_receiver_fn(self):
        return self._serving_input_receiver_fn

    @property
    def metric_name(self):
        return self._metric_name

    @property
    def save_max(self):
        return self._save_max

    @property
    def ckpt_path(self):
        return self._ckpt_path

    @property
    def best_metric_var(self):
        return self._best_metric_var

    @property
    def saver(self):
        return self._saver

    @property
    def sess(self):
        return self._sess

    @property
    def assign_op(self):
        return self._assign_op

    @property
    def init_op(self):
        return self._init_op

    @property
    def best_metric_val(self):
        return self._best_metric_val

    def feed_dict(self, assign_val):
        return {self._assign_val_ph: assign_val}

    def _build_graph(self):
        graph = tf.Graph()

        with graph.as_default():
            self._best_metric_var = tf.get_variable('best_metric',
                                                    shape=(),
                                                    dtype=tf.float32,
                                                    trainable=False,
                                                    initializer=tf.initializers.constant(
                                                        -float('inf') if self.save_max else float('inf')))
            self._saver = tf.train.Saver(var_list=[self.best_metric_var])
            self._assign_val_ph = tf.placeholder(tf.float32, shape=())
            self._assign_op = tf.assign(self.best_metric_var, self._best_metric_var)

            self._init_op = tf.global_variables_initializer()

        self._sess = tf.Session(graph=graph)

    def _restore(self):

        if tf.train.checkpoint_exists(self.ckpt_path):
            self.saver.restore(self.sess, self.ckpt_path)
        else:
            self.sess.run(self.init_op)

        self._best_metric_val = self.sess.run(self.best_metric_var)

    def check_n_update(self, metrics):
        if self.metric_name not in metrics:
            raise ValueError('Metric variable named `{}` is not found'.format(self.metric_name))

        cur_metric_val = metrics[self.metric_name]

        if (cur_metric_val > self.best_metric_val and self.save_max) or \
                (cur_metric_val < self.best_metric_val and not self.save_max):
            tf.logging.info('Value of {metric_name}: {metric_val} achieved the best value: {best_val} ever yet'.format(
                metric_name=self.metric_name, metric_val=cur_metric_val, best_val=self.best_metric_val))
            self._update(cur_metric_val)
            exported_dir = self.export()
            tf.logging.info('New model is exported to {}'.format(exported_dir))

    def _update(self, val):
        self.sess.run(self.assign_op, feed_dict=self.feed_dict(val))
        self._best_metric_val = val

        self.saver.save(self.sess, self.ckpt_path)

    def export(self):
        exported_dir = self.estimator.export_savedmodel(self.estimator.model_dir,
                                                        self.serving_input_receiver_fn).decode('utf-8')

        ckpt_prefix = tf.train.latest_checkpoint(self.estimator.model_dir)
        for f in tf.gfile.Glob(ckpt_prefix + '.*'):
            copy(f, exported_dir)

        return exported_dir


class ImageSaverHook(tf.train.SessionRunHook):
    def __init__(self,
                 images,
                 image_dir):
        self.run_args = dict(
            map(lambda item: (item[0], tf.image.convert_image_dtype(item[1], tf.uint8)), images.items()))
        self.image_dir = image_dir
        self.iter = 0

        if not tf.gfile.Exists(self.image_dir):
            tf.gfile.MakeDirs(self.image_dir)

        tf.logging.info('ImageSaverHook: {}'.format(self.run_args))

    def before_run(self, run_context: tf.train.SessionRunContext):
        run_args = dict(self.run_args)
        run_args.update({'global_step': tf.train.get_or_create_global_step()})
        return tf.train.SessionRunArgs(run_args)

    def after_run(self,
                  run_context: tf.train.SessionRunContext,  # pylint: disable=unused-argument
                  run_values: tf.train.SessionRunValues):
        global_step = run_values.results['global_step']
        for k in self.run_args.keys():
            images = run_values.results[k]
            encoded = encode(images)
            with open(os.path.join(self.image_dir,
                                   '{key}_{gs:07d}_{iter:03d}.jpg'.format(
                                       key=k, gs=global_step, iter=self.iter)), 'wb') as f:
                f.write(encoded)

        self.iter += 1
