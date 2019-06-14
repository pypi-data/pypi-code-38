"""
    Initializers for runner
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import tensorflow as tf

from tflibs.utils import list_modules, import_module, log_parse_args
from tflibs.model import Model


class BaseInitializer:
    def add_arguments(self, argparser: argparse.ArgumentParser):
        raise NotImplementedError

    def handle(self, parse_args: argparse.Namespace, unknown) -> tuple:
        raise NotImplementedError


class DatasetInitializer(BaseInitializer):
    def __init__(self, dataset_pkg='datasets.dataset'):
        self._dataset_pkg = dataset_pkg

    def _list_datasets(self) -> list:
        return list_modules(self._dataset_pkg.replace('.', '/'))

    def _dataset_factory(self, name):
        return import_module(self._dataset_pkg, name).export

    def add_arguments(self, argparser):
        """
        Adds arguments

        * --dataset-dir
        * --dataset-name

        :param argparse.ArgumentParser argparser: Argument parser used to add arguments
        """
        argparser.add_argument('--dataset-dir',
                               required=True,
                               type=str,
                               help='The directory where the dataset files are stored.')
        argparser.add_argument('--dataset-name',
                               required=True,
                               type=str,
                               help='The name of a dataset.',
                               choices=self._list_datasets())

    def handle(self, parse_args, unknown):
        """
        Handles arguments.

        Exhausts `--dataset-name` and `--dataset-dir`, and generates `dataset`.

        Parses dataset-specific arguments.

        See: `tflib.datasets.BaseDataset.add_arguments() <./Dataset.html#tflibs.datasets.dataset.BaseDataset.add_arguments>`_

        :param argparse.Namespace parse_args: Parsed arguments.
        :param list unknown: A list of unknown arguments. Exhaust these list.
        :return: A tuple of a dict of handled arguments and unknown arguments.
        :rtype: tuple
        """
        dataset_name = parse_args.dataset_name
        dataset_dir = parse_args.dataset_dir

        del parse_args.dataset_name
        del parse_args.dataset_dir

        dataset_cls = self._dataset_factory(dataset_name)

        # Parse dataset-specific arguments
        parser = argparse.ArgumentParser()
        dataset_cls.add_arguments(parser)
        parse_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(parse_args, 'Dataset arguments')

        dataset = dataset_cls(dataset_dir, **vars(parse_args))

        return {'dataset': dataset}, unknown


class ModelInitializer(BaseInitializer):
    def __init__(self, model_pkg='models'):
        self._model_pkg = model_pkg

    def _model_factory(self, name):
        return import_module(self._model_pkg, name).export

    def _list_models(self):
        return list_modules(self._model_pkg)

    def add_arguments(self, argparser):
        """
        Adds arguments.

        * --model-name

        :param argparse.ArgumentParser argparser: Argument parser used to add arguments.
        """
        argparser.add_argument('--model-name',
                               type=str,
                               required=True,
                               help='The name of the model to use.',
                               choices=self._list_models())

    def handle(self, parse_args, unknown):
        """
        Handles arguments.

        Exhausts `--model-name` and generates `model_cls`.

        :param argparse.Namespace parse_args: Parsed arguments.
        :param list unknown: A list of unknown arguments. Exhaust these list.
        :return: A tuple of a dict of handled arguments and unknown arguments.
        :rtype: tuple
        """
        model_name = parse_args.model_name

        del parse_args.model_name

        model_cls = self._model_factory(model_name)

        # Parse model-specific arguments
        parser = argparse.ArgumentParser()
        model_cls.add_model_args(parser, parse_args)
        model_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(model_args, 'Model arguments')

        return {'model_cls': model_cls,
                'model_args': vars(model_args)}, unknown


class TrainInitializer(ModelInitializer):
    def add_arguments(self, argparser):
        """
        Adds arguments.

        Adds arguments of `ModelInitializer`.

        * --model-name

        and

        * --save-steps
        * --keep-checkpoint-max
        * --log-steps
        * --random-seed
        * --train-iters

        :param argparse.ArgumentParser argparser: Argument parser used to add arguments.
        """
        ModelInitializer.add_arguments(self, argparser)

        argparser.add_argument('--save-steps',
                               type=int,
                               default=1000,
                               help='The number of steps to save the model.')
        argparser.add_argument('--keep-checkpoint-max',
                               type=int,
                               default=500,
                               help='The maximum number of checkpoint file to keep.')
        argparser.add_argument('--log-steps',
                               type=int,
                               default=10,
                               help='The number of steps to log the progress.')
        argparser.add_argument('--random-seed',
                               type=int,
                               default=1,
                               help='Random seed')
        argparser.add_argument('--train-iters',
                               type=int,
                               default=200000,
                               help='Maximum number of training iterations to perform.')
        argparser.add_argument('--train-batch-size',
                               type=int,
                               default=1,
                               help='Batch size for training')
        argparser.add_argument('--eval-batch-size',
                               type=int,
                               default=1,
                               help='Batch size for evaluation')
        argparser.add_argument('--no-soft-placement',
                               action='store_true',
                               help='The name of the model to use.')
        argparser.add_argument('--num-towers',
                               type=int,
                               default=1,
                               help='The number of towers for data augmentation.')

    def handle(self, parse_args, unknown):
        """
        Handles arguments.

        Parses model-specific arguments.

        * model_args: Common arguments. See: `tflib.model.Model.add_model_args() <./tflibs.model.html#tflibs.model.Model.add_model_args>`_
        * train_args: Train arguments. See: `tflib.model.Model.add_train_args() <./tflibs.model.html#tflibs.model.Model.add_train_args>`_
        * eval_args: Evaluation arguments. See: `tflib.model.Model.add_eval_args() <./tflibs.model.html#tflibs.model.Model.add_eval_args>`_

        :param argparse.Namespace parse_args: Parsed arguments.
        :param list unknown: A list of unknown arguments. Exhaust these list.
        :return: A tuple of a dict of handled arguments and unknown arguments.
        :rtype: tuple
        """
        save_steps = parse_args.save_steps
        log_steps = parse_args.log_steps
        keep_checkpoint_max = parse_args.keep_checkpoint_max
        random_seed = parse_args.random_seed
        no_soft_placement = parse_args.no_soft_placement
        num_towers = parse_args.num_towers
        train_batch_size = parse_args.train_batch_size

        del parse_args.save_steps
        del parse_args.log_steps,
        del parse_args.keep_checkpoint_max
        del parse_args.random_seed
        del parse_args.no_soft_placement
        del parse_args.num_towers
        del parse_args.train_batch_size

        session_config = tf.ConfigProto(log_device_placement=False,
                                        allow_soft_placement=not no_soft_placement)

        run_config = tf.estimator.RunConfig(session_config=session_config,
                                            save_summary_steps=save_steps,
                                            save_checkpoints_steps=save_steps,
                                            log_step_count_steps=log_steps,
                                            keep_checkpoint_max=keep_checkpoint_max,
                                            tf_random_seed=random_seed)

        if num_towers > 1:
            if train_batch_size % num_towers != 0:
                raise ValueError('`train_batch_size` should be divided by `num_towers`.')
            train_batch_size = train_batch_size // num_towers

            mirrored_strategy = tf.distribute.MirroredStrategy(
                cross_device_ops=tf.contrib.distribute.AllReduceCrossDeviceOps(all_reduce_alg='hcopy'))
            run_config = run_config.replace(train_distribute=mirrored_strategy)

        handled_args, unknown = ModelInitializer.handle(self, parse_args, unknown)

        model_cls = handled_args['model_cls']  # type: Model
        model_args = handled_args['model_args']

        # Parse model-specific train arguments
        parser = argparse.ArgumentParser()
        model_cls.add_train_args(parser, parse_args)
        train_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(train_args, 'Train arguments')

        # Parse model-specific eval arguments
        parser = argparse.ArgumentParser()
        model_cls.add_eval_args(parser, parse_args)
        eval_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(eval_args, 'Eval arguments')

        train_args = vars(train_args)
        train_args.update({'train_iters': parse_args.train_iters,
                           'train_batch_size': train_batch_size})

        eval_args = vars(eval_args)
        eval_args.update({'eval_batch_size': parse_args.eval_batch_size})

        model_params = {
            'model_args': model_args,
            'train_args': train_args,
            'eval_args': eval_args,
        }

        estimator = tf.estimator.Estimator(
            model_cls.model_fn,
            model_dir=parse_args.job_dir,
            config=run_config,
            params=model_params)

        return {'estimator': estimator,
                'train_batch_size': train_batch_size,
                'eval_batch_size': parse_args.eval_batch_size,
                'model_cls': model_cls,
                'train_map_fn': model_cls.make_map_fn('train', **model_args),
                'eval_map_fn': model_cls.make_map_fn('eval', **model_args),
                'serving_input_receiver_fn': model_cls.make_map_fn('predict', **model_args), }, unknown


class EvalInitializer(ModelInitializer):
    def add_arguments(self, argparser):
        """
        Adds arguments.

        Adds arguments of `ModelInitializer`.

        * --model-name

        :param argparse.ArgumentParser argparser: Argument parser used to add arguments.
        """
        ModelInitializer.add_arguments(self, argparser)

        argparser.add_argument('--eval-batch-size',
                               type=int,
                               default=1,
                               help='Batch size for evaluation')
        argparser.add_argument('--allow-soft-placement',
                               action='store_true',
                               help='The name of the model to use.')

    def handle(self, parse_args, unknown):
        """
        Handles arguments.

        Parses model-specific arguments.

        * model_args: Common arguments. See: `tflib.model.Model.add_model_args() <./tflibs.model.html#tflibs.model.Model.add_model_args>`_
        * eval_args: Evaluation arguments. See: `tflib.model.Model.add_eval_args() <./tflibs.model.html#tflibs.model.Model.add_eval_args>`_

        :param argparse.Namespace parse_args: Parsed arguments.
        :param list unknown: A list of unknown arguments. Exhaust these list.
        :return: A tuple of a dict of handled arguments and unknown arguments.
        :rtype: tuple
        """
        handled_args, unknown = ModelInitializer.handle(self, parse_args, unknown)

        model_cls = handled_args['model_cls']

        # Parse model-specific arguments
        parser = argparse.ArgumentParser()
        model_cls.add_model_args(parser, parse_args)
        model_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(model_args, 'Model arguments')

        # Parse model-specific eval arguments
        parser = argparse.ArgumentParser()
        model_cls.add_eval_args(parser, parse_args)
        eval_args, unknown = parser.parse_known_args(unknown)
        log_parse_args(eval_args, 'Eval arguments')

        eval_args = vars(eval_args)
        eval_args.update({'eval_batch_size': parse_args.eval_batch_size})

        model_params = {
            'model_args': vars(model_args),
            'eval_args': eval_args,
        }

        allow_soft_placement = parse_args.allow_soft_placement

        del parse_args.allow_soft_placement

        session_config = tf.ConfigProto(log_device_placement=False,
                                        allow_soft_placement=allow_soft_placement)

        run_config = tf.estimator.RunConfig().replace(session_config=session_config)

        estimator = tf.estimator.Estimator(
            model_cls.model_fn,
            model_dir=parse_args.job_dir,
            config=run_config,
            params=model_params)

        return {'estimator': estimator,
                'eval_batch_size': parse_args.eval_batch_size,
                'model_cls': model_cls,
                'eval_map_fn': model_cls.make_map_fn('eval', **vars(model_args))}, unknown
