import os

import tensorflow as tf
import copy

from seq2label import utils


def train_model(train_inpf, eval_inpf, config, model_fn, model_name):
    estimator_params = copy.deepcopy(config)

    # indices = [idx for idx, tag in enumerate(config['tags_data']) if tag.strip() != 'O']
    # num_tags = len(indices) + 1
    # estimator_params['_indices'] = indices
    # estimator_params['_num_tags'] = num_tags

    cfg = tf.estimator.RunConfig(save_checkpoints_secs=config['save_checkpoints_secs'])

    model_specific_name = '{model_name}-{batch_size}-{learning_rate}-{max_steps}-{max_steps_without_increase}'.format(
        model_name=model_name,
        batch_size=config['batch_size'],
        learning_rate=config['learning_rate'],
        max_steps=config['max_steps'],
        max_steps_without_increase=config['max_steps_without_increase']
    )

    instance_model_dir = os.path.join(config['model_dir'], model_specific_name)

    if config['use_tpu']:
        tpu_cluster_resolver = tf.contrib.cluster_resolver.TPUClusterResolver(
            tpu=config['tpu_name'],
            zone=config['tpu_zone'],
            project=config['gcp_project']
        )

        run_config = tf.contrib.tpu.RunConfig(
            cluster=tpu_cluster_resolver,
            model_dir=instance_model_dir,
            session_config=tf.ConfigProto(
                allow_soft_placement=True, log_device_placement=True),
            tpu_config=tf.contrib.tpu.TPUConfig(),
        )

        tpu_estimator_params = copy.deepcopy(estimator_params)
        # remove reserved keys
        # tpu_estimator_params['train_batch_size'] = tpu_estimator_params['batch_size']
        del tpu_estimator_params['batch_size']
        # del tpu_estimator_params['context']

        estimator = tf.contrib.tpu.TPUEstimator(model_fn=model_fn, params=tpu_estimator_params, config=run_config, use_tpu=True,
                                                train_batch_size=estimator_params['batch_size'],
                                                eval_batch_size=estimator_params['batch_size'],
                                                predict_batch_size=estimator_params['batch_size']
                                                )
    else:
        estimator = tf.estimator.Estimator(model_fn, instance_model_dir, cfg, estimator_params)


    # Path(estimator.eval_dir()).mkdir(parents=True, exist_ok=True)
    utils.create_dir_if_needed(estimator.eval_dir())


    # hook_params = params['hook']['stop_if_no_increase']
    # hook = tf.contrib.estimator.stop_if_no_increase_hook(
    #     estimator, 'f1',
    #     max_steps_without_increase=hook_params['max_steps_without_increase'],
    #     min_steps=hook_params['min_steps'],
    #     run_every_secs=hook_params['run_every_secs']
    # )

    # build hooks from config
    train_hook = []
    for i in config.get('train_hook', []):
        class_ = class_from_module_path(i['class'])
        train_hook.append(class_(**i['params']))

    eval_hook = []
    for i in config.get('eval_hook', []):
        class_ = class_from_module_path(i['class'])
        eval_hook.append(class_(**i['params']))

    if eval_inpf:
        train_spec = tf.estimator.TrainSpec(input_fn=train_inpf, hooks=train_hook, max_steps=config['max_steps'])
        eval_spec = tf.estimator.EvalSpec(input_fn=eval_inpf, throttle_secs=config['throttle_secs'], hooks=eval_hook)
        evaluate_result, export_results = tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)
    else:
        estimator.train(input_fn=train_inpf, hooks=train_hook, max_steps=config['max_steps'])
        evaluate_result, export_results = {}, None

    # export saved_model
    feature_spec = {
        'words': tf.placeholder(tf.string, [None, config['max_seq_length']]),
    }

    if config.get('forced_saved_model_dir'):
        instance_saved_dir = config.get('forced_saved_model_dir')
    else:
        instance_saved_dir = os.path.join(config['saved_model_dir'], model_specific_name)

    utils.create_dir_if_needed(instance_saved_dir)

    serving_input_receiver_fn = tf.estimator.export.build_raw_serving_input_receiver_fn(feature_spec)
    raw_final_saved_model = estimator.export_saved_model(
        instance_saved_dir,
        serving_input_receiver_fn,
        # assets_extra={
        #     'tags.txt': 'data/tags.txt',
        #     'vocab.txt': 'data/unicode_char_list.txt'
        # }
    )

    final_saved_model = raw_final_saved_model.decode('utf-8')

    return evaluate_result, export_results, final_saved_model