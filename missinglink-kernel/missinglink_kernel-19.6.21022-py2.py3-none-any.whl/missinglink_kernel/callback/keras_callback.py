# -*- coding: utf-8 -*-
from __future__ import absolute_import

import copy
import warnings
from contextlib import contextmanager

import numpy as np
from missinglink_kernel.callback.phase import PhaseTest
from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine, has_base_class, calc_tf_variable_value
from .base_callback import BaseCallback
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface, GradCAMInterface, ImageDimOrdering, VisualBackPropInterface
from .settings import HyperParamTypes, MetricPhasePrefixes, AlgorithmTypes


class KerasCallback(BaseCallback, ModelHashInterface, GradCAMInterface, VisualBackPropInterface):
    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        super(KerasCallback, self).__init__(
            owner_id, project_token, stopped_callback=stopped_callback, framework='keras', **kwargs)
        self.token = project_token
        self.current_epoch = 0
        self.params = {}
        self.model = None

        warnings.filterwarnings('ignore', r'Method on_batch_begin\(\) is slow compared to the batch update')
        warnings.filterwarnings('ignore', r'Method on_batch_end\(\) is slow compared to the batch update')

    # Deprecated. To support Keras v1
    def _set_params(self, params):
        self.params = self._params_v2_from_v1(params)

    # Deprecated. To support Keras v1
    def _set_model(self, model):
        self.model = model

    def set_params(self, params):
        self.params = params

    def set_model(self, model):
        self.model = model

    @classmethod
    def __prefix_metric(cls, metric, is_test):
        if is_test:
            return MetricPhasePrefixes.TEST + metric

        keras_validation_prefix_string = 'val_'
        if metric.startswith(keras_validation_prefix_string):
            return MetricPhasePrefixes.VAL + metric[len(keras_validation_prefix_string):]

        return MetricPhasePrefixes.TRAIN + metric

    def on_train_begin(self, logs=None):
        params = copy.copy(self.params)

        if 'steps' in params and params['steps'] is None:
            del params['steps']

        self.set_hyperparams(
            total_epochs=params.get('epochs'),
            batch_size=params.get('batch_size'),
            samples_count=params.get('samples') or params.get("sample"))

        if 'metrics' in params:
            params['metrics'] = [self.__prefix_metric(name, is_test=False) for name in params.get('metrics')]

        self._extract_hyperparams_from_optimizer(self.model.optimizer)
        structure_hash = self._get_structure_hash(self.model)
        self.train_begin(params, structure_hash=structure_hash, throw_exceptions=False)

    def on_train_end(self, logs=None):
        self._train_end(metricData=self._latest_metrics)

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch

        self.epoch_begin(epoch)

    # noinspection PyBroadException
    def on_epoch_end(self, epoch, logs=None):
        try:
            model_hash = self.get_weights_hash(self.model)
        except Exception:
            self.logger.exception('failed to calc weights hash')
            model_hash = None

        ml_prefixed_metrics_dict = {self.__prefix_metric(name, is_test=False): value for name, value in logs.items()}
        self.epoch_end(epoch, ml_prefixed_metrics_dict, weights_hash=model_hash)

    def on_batch_begin(self, batch, logs=None):
        self.batch_begin(batch, self.current_epoch)

    def _is_last_batch(self, batch):
        if 'samples' not in self.params or 'batch_size' not in self.params:
            return False

        batches = self.params['samples'] / self.params['batch_size']
        return batch == batches - 1

    def _is_last_epoch(self, epoch):
        return epoch == self.params['epochs'] - 1

    def on_batch_end(self, batch, logs=None):
        metric_data = {metric: logs[metric] for metric in self.params['metrics'] if metric in logs}
        ml_prefixed_metrics_dict = {self.__prefix_metric(name, is_test=False): value for name, value in metric_data.items()}
        self.batch_end(batch, self.current_epoch, ml_prefixed_metrics_dict)

    def on_train_batch_begin(self, batch, logs=None):
        # For backwards compatibility
        self.on_batch_begin(batch, logs=logs)

    def on_train_batch_end(self, batch, logs=None):
        # For backwards compatibility
        self.on_batch_end(batch, logs=logs)

    @classmethod
    def calculate_weights_hash(cls, net):
        weight_hashes = []
        for layer in net.layers:
            weights = layer.get_weights()
            if weights is None:
                continue

            for weight in weights:
                weight_hashes.append(hasharray(weight))

        return cls._WEIGHTS_HASH_PREFIX + hashcombine(*weight_hashes)

    def variable_to_value(self, variable):
        var_classes = ['Variable', 'RefVariable']
        is_tf_var = variable.__class__.__name__ in var_classes or has_base_class(variable, var_classes)

        if is_tf_var:
            try:
                from .vis.dynamic_import import DynamicImport

                dynamic_import = DynamicImport(self.model)

                if dynamic_import.module.__name__ == 'keras':
                    keras_backend = dynamic_import.bring('backend')
                else:
                    keras_backend = dynamic_import.bring('keras').backend

                return keras_backend.eval(variable)
            except Exception:
                warnings.warn("was not able to get variable %s" % variable.name)
                return calc_tf_variable_value(variable)

        return super(KerasCallback, self).variable_to_value(variable)

    def _get_feature_maps(self, model, image, shape=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)

        layer_indexes = [ind for ind, el in enumerate(model.layers) if isinstance(el, Convolution2D)]
        layers = [model.layers[li].output for li in layer_indexes]
        get_feature = keras_backend.function([model.layers[0].input], layers)
        output = model.predict(np.expand_dims(input_, axis=0))
        feature_maps = get_feature([[input_]])
        return feature_maps, output

    @classmethod
    def _get_input_dim(cls, model):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        if channels_first:
            # it means we have NCHW ordering
            _, depth, height, width = model.input_shape
        else:
            # we have NHWC ordering
            _, height, width, depth = model.input_shape
        return depth, height, width

    @classmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        Lambda = dynamic_import.bring('layers.core.Lambda')
        Sequential = dynamic_import.bring('models.Sequential')
        K = dynamic_import.bring('backend')

        def normalize(x):
            # utility function to normalize a tensor by its L2 norm
            return x / (K.sqrt(K.mean(K.square(x))) + 1e-5)

        def target_category_loss(x, category_index, nb_classes):
            return K.batch_dot(x, K.one_hot([category_index], nb_classes), axes=(1, 1))

        def target_category_loss_output_shape(input_shape):
            return input_shape

        def target_layer(x):
            return target_category_loss(x, pred_class, scores.shape[0])

        pred_class = np.argmax(scores)
        result_model = Sequential()
        result_model.add(model)
        result_model.add(Lambda(target_layer, output_shape=target_category_loss_output_shape))
        conv_layer_indexes = [i for i, layer in enumerate(model.layers) if isinstance(layer, Convolution2D)]
        if not conv_layer_indexes:
            raise MissingLinkException("Unable to find convolutional layer in the model!")

        conv_output = model.layers[conv_layer_indexes[-1]].output
        loss = K.sum(result_model.layers[-1].output)
        grads = normalize(K.gradients(loss, conv_output)[0])
        gradient_function = K.function([result_model.layers[0].input], [conv_output, grads])
        output, grads_val = gradient_function([np.expand_dims(input_, axis=0)])

        dim_ordering = K.image_dim_ordering()
        channels_first = dim_ordering == 'th'
        axis = (1, 2) if channels_first else (0, 1)
        a_weights = np.mean(grads_val[0], axis=axis)

        return output, a_weights

    def _get_prediction(self, model, image, shape=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)
        probs = model.predict(np.array([input_]))
        probs = np.squeeze(probs)
        return input_, probs

    def process_image(self, path=None, model=None, upload_images=None, seed_image=None):
        from .vis.dynamic_import import DynamicImport

        warnings.warn("This method is deprecated. use 'generate_grad_cam' instead", DeprecationWarning)
        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        dim_order = ImageDimOrdering.NCHW if channels_first else ImageDimOrdering.NHWC

        self.generate_grad_cam(path, model, input_array=seed_image, dim_order=dim_order)

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order, logger=self.logger)

        except MissingLinkException:
            self.logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            images = self._prepare_images_payload(images_data, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order,
                                            logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            images = self._prepare_images_payload(result, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    # region ModelHashInterface

    def get_weights_hash(self, net):
        return self.calculate_weights_hash(net)

    @ModelHashInterface.wrap_all_get_structure_hash_exceptions
    def _get_structure_hash(self, net):
        layers_repr = []
        for i, layer in enumerate(net.layers):
            inbound_nodes = layer._inbound_nodes if hasattr(layer, '_inbound_nodes') else layer.inbound_nodes
            if not inbound_nodes:
                continue

            inbound_node_shapes = [tuple(layer.get_input_shape_at(index)) for index in range(len(inbound_nodes))]
            inbound_node_shapes = tuple(inbound_node_shapes) if len(inbound_node_shapes) > 1 else inbound_node_shapes[0]

            layer_bias = getattr(layer, 'use_bias', None)
            layer_type = type(layer)
            layers_repr.append((layer_type, inbound_node_shapes, layer_bias))

        return self._hash(tuple(layers_repr))

    # endregion
    @classmethod
    def _params_v2_from_v1(cls, params_v1):
        params_v2 = params_v1.copy()
        params_v2['epochs'] = params_v1['nb_epoch']
        params_v2['samples'] = params_v1['nb_sample']
        return params_v2

    def _extract_hyperparams_from_optimizer(self, optimizer):
        optimizer_hyperparams = {
            'SGD': ['lr', 'momentum', 'decay', 'nesterov'],
            'RMSprop': ['lr', 'rho', 'epsilon', 'decay'],
            'Adagrad': ['lr', 'epsilon', 'decay'],
            'Adadelta': ['lr', 'rho', 'epsilon', 'decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Nadam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'schedule_decay'],
        }
        hyperparam_names = {
            'lr': 'learning_rate',
            'decay': 'learning_rate_decay',
        }

        self.set_hyperparams(optimizer_algorithm=optimizer.__class__.__name__)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_hyperparams, hyperparam_names)

    @contextmanager
    def test(self, model=None, callback=None, generate_confusion_matrix=True, name=None):
        if not self.has_experiment:
            self.new_experiment()

        model = model or self.model
        self.set_model(model)

        phase = PhaseTest(MetricPhasePrefixes.TEST)

        self._patch_evaluate_generator(phase)
        self._patch_test_loop(phase, name=name)
        self._patch_test_function(generate_confusion_matrix, callback)

        yield phase

        self._unpatch_evaluate_generator()
        self._unpatch_test_loop()
        self._unpatch_test_function()

        self._on_test_end(phase)

    def _create_test_function(self, original_test_function, generate_confusion_matrix, callback=None):
        def invoke_callback(y, y_true):
            if callable(callback):
                return callback(y, y_true)

            return y, y_true

        def test_function(ins_batch):
            number_of_inputs = len(self.model.inputs)
            batch_size = len(ins_batch[0])

            x = ins_batch[:number_of_inputs]
            y_true = ins_batch[number_of_inputs:number_of_inputs + number_of_inputs]

            y = self.model.predict(x, batch_size=batch_size)

            output_y, y_true = invoke_callback(y, y_true[0])

            number_of_outputs = len(self.model.inputs)

            if number_of_outputs == 1:
                output_y = [output_y]

            result = original_test_function(ins_batch)

            yy = output_y[0]
            predictions = yy.argmax(axis=-1)
            probabilities = yy.max(axis=-1)
            expected = np.argmax(y_true, axis=1)

            expected = expected.tolist()
            predictions = predictions.tolist()
            probabilities = probabilities.tolist()

            if generate_confusion_matrix:
                self._test_iteration_end(expected, predictions, probabilities)
            else:
                self._test_iteration_end([], [], [])

            return result

        return test_function

    def _on_test_begin(self, steps, name=None):
        weights_hash = self.get_weights_hash(self.model)

        if weights_hash is None:
            # TODO warn
            return

        self._test_begin(steps, weights_hash, name=name)

    def _on_test_end(self, phase):
        ml_prefixed_metrics_dict = {name: value for name, value in phase.get_average_metrics().items()}

        self._test_end(metric_data=ml_prefixed_metrics_dict)

    def __wrap_test_results(self, phase, steps, caller, name=None):
        self._on_test_begin(steps, name=name)

        results = caller()

        if not isinstance(results, (list, tuple)):
            actual_results = [results]
        else:
            actual_results = results

        metrics_names = getattr(self.model, 'metrics_names', None) or []
        for metrics_name, val in zip(metrics_names, actual_results):
            phase.add_metric(metrics_name, val, is_custom=False)

        return results

    def _create_ml_evaluate_generator(self, phase):
        def _ml_evaluate_generator(
                generator,
                steps=None,
                max_queue_size=10,
                workers=1,
                use_multiprocessing=False):

            return self.__wrap_test_results(
                phase,
                steps,
                lambda: self._evaluate_generator(
                    generator, steps, max_queue_size=max_queue_size, workers=workers, use_multiprocessing=use_multiprocessing))

        return _ml_evaluate_generator

    @classmethod
    def __calc_steps_if_possible(cls, ins, batch_size, steps):
        temp_steps = steps
        if steps is None:
            test_samples_count = ins[0].shape[0] if ins and hasattr(ins[0], 'shape') else batch_size
            temp_steps = int(np.ceil(test_samples_count / float(batch_size)))

        return temp_steps

    _not_a_value = object()

    @classmethod
    def search_param(cls, names, args_index, current_args, current_kwargs):
        if len(current_args) > args_index:
            return current_args[args_index]

        for name in names:
            value = current_kwargs.get(name, cls._not_a_value)

            if value is not cls._not_a_value:
                return value

    def __ml_test_loop_wrap(self, phase, is_method_bounded, call_test_loop, name=None):
        def __ml_test_loop(ins_index, batch_size_index, steps_index):
            def wrap(*args, **kwargs):
                ins = self.search_param(('inputs', 'ins'), ins_index, args, kwargs)
                batch_size = self.search_param(('batch_size',), batch_size_index, args, kwargs)
                steps = self.search_param(('steps',), steps_index, args, kwargs)

                temp_steps = self.__calc_steps_if_possible(ins, batch_size, steps)

                return self.__wrap_test_results(phase, temp_steps, lambda: call_test_loop(*args, **kwargs), name=name)

            return wrap

        _ml_test_loop = __ml_test_loop(2, 3, 5)
        _ml_test_loop_bounded = __ml_test_loop(1, 2, 4)

        return _ml_test_loop_bounded if is_method_bounded else _ml_test_loop

    def _get_training_model(self):
        if hasattr(self.model, 'test_function'):
            # Sequential.model is deprecated and throws a warning since 2018-05.
            # So prefer not to use `model.model` if possible.
            # https://github.com/keras-team/keras/blob/8e8f989b850d37a4cbec7a0409343262bd963d0d/keras/engine/sequential.py#L109
            return self.model

        if hasattr(self.model, 'model') and hasattr(self.model.model, 'test_function'):
            return self.model.model

        return self.model

    def _patch_evaluate_generator(self, phase):
        training_model = self._get_training_model()

        self._evaluate_generator = training_model.evaluate_generator
        training_model.evaluate_generator = self._create_ml_evaluate_generator(phase)

    @classmethod
    def __import_training_arrays(cls, training_model):
        from missinglink_kernel.callback.vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(training_model)
        try:
            training_arrays = dynamic_import.bring('engine.training_arrays')
        except AttributeError:
            from tensorflow.python.keras.engine import training_arrays

        return training_arrays

    def _unpatch_test_loop(self):
        training_model = self._get_training_model()

        def unpatch_if_possible(obj, name):
            if not hasattr(obj, name):
                return False

            setattr(obj, name, self.__prev_test_loop)
            del self.__prev_test_loop

            return True

        if not unpatch_if_possible(training_model, '_test_loop'):
            training_arrays = self.__import_training_arrays(training_model)

            unpatch_if_possible(training_arrays, 'test_loop')

    def _patch_test_loop(self, phase, call_test_loop=None, name=None):
        training_model = self._get_training_model()

        def patch_if_possible(obj, method_name):
            if not hasattr(obj, method_name):
                return None

            prev_test_loop = getattr(obj, method_name)

            def is_bound(method):
                return hasattr(method, 'im_self') or hasattr(method, '__self__')

            is_method_bounded = is_bound(prev_test_loop)

            ml_test_loop = self.__ml_test_loop_wrap(phase, is_method_bounded, call_test_loop or prev_test_loop,
                                                    name=name)
            setattr(obj, method_name, ml_test_loop)

            self.__prev_test_loop = prev_test_loop

            if is_method_bounded:
                def ml_test_loop_function(_self, f, ins, batch_size=None, verbose=0, steps=None):
                    return ml_test_loop(f, ins, batch_size, verbose, steps)

                return ml_test_loop_function

            # noinspection PyUnresolvedReferences
            return ml_test_loop

        # noinspection PyProtectedMember
        method_method = patch_if_possible(training_model, '_test_loop')
        if not method_method:  # keras 2.2
            training_arrays = self.__import_training_arrays(training_model)

            method_method = patch_if_possible(training_arrays, 'test_loop')
            if not method_method:
                self.logger.warning('failed to patch test loop')

        return method_method

    def _patch_test_function(self, generate_confusion_matrix, callback=None):
        training_model = self._get_training_model()

        # noinspection PyProtectedMember
        training_model._make_test_function()

        temp_test = training_model.test_function

        training_model.test_function = self._create_test_function(temp_test, generate_confusion_matrix, callback)

    def _unpatch_evaluate_generator(self):
        training_model = self._get_training_model()

        training_model.evaluate_generator = self._evaluate_generator
        del self._evaluate_generator

        training_model.test_function = None

    def _unpatch_test_function(self):
        training_model = self._get_training_model()

        training_model.test_function = None
