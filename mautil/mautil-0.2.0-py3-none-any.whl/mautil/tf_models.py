import time, logging, numpy as np, json, os
from copy import deepcopy
from collections import namedtuple
from collections import OrderedDict, defaultdict

from .basic_model import BasicModel, InputFeature, LossHist
from .data_reader import create_data_reader
from . import tf_util
from . import util

import tensorflow as tf

class SessionRunHook(tf.train.SessionRunHook):
    def __init__(self, model):
        self._model = model

    def before_run(self, run_context):
        return self._model.before_run(run_context)

    def after_run(self, run_context, run_values):
        self._model.after_run(runcontext, run_values)


class TF(BasicModel, tf.train.SessionRunHook):
    cfg = deepcopy(BasicModel.cfg)
    cfg.verbose = 30
    cfg.global_step = None
    cfg.batch_reader_cfg = {'process_mode': 'T'}
    cfg.gradient_clip = None
    cfg.batch_reader = 'BatchReader'
    cfg.dropout = None
    cfg.tf_qsize = 4
    cfg.keep_checkpoint_every_n_hours = 1000000000
    cfg.save_keep = 1000000000
    cfg.use_tpu = False
    cfg.tpu_name = None
    cfg.warm_start_path = None  # used by tpu
    cfg.tpu_zone = None
    cfg.gcp_project = None
    cfg.num_core_per_host = 1
    cfg.num_hosts = 1
    cfg.tpu_loop_iterations = 2

    def __init__(self, name = 'TF', cfg={}, batch_reader=None):
        super(TF, self).__init__(name, cfg)
        if self.cfg.use_tpu:
            self.cfg.use_tf_estimator=True
        self._input_features = self._init_input_features()
        if batch_reader is None:
            batch_reader = self.cfg.batch_reader

        if isinstance(batch_reader, str):
            self.batch_reader = create_data_reader(batch_reader, 'batch_reader', self.cfg.seed, self.gen_fname(''), **self.cfg.batch_reader_cfg)
        else:
            self.batch_reader = batch_reader
        self._run_phase = 'train'
        self._loss_hist = None
        tf_util.set_tfloglevel(self.cfg.tf_loglevel)

    def begin(self):
        self._loss_hist = LossHist()
        self._run_step = 0

    def after_create_session(self, session, coord):
        is_training = session.run(self._training_plh)
        if is_training:
            self._run_phase = 'train'
        elif self._run_phase != 'predict':
            self._run_phase = 'validate'

    def before_run(self, run_context):
        self._run_step += 1
        if self._run_phase == 'train':
            fetches = self.train_nodes

        elif self._run_phase == 'validate':
            fetches = self.validate_nodes

        elif self._run_phase == 'predict':
            fetches = self._pred_dict
        else:
            raise NotImplemented
        run_args = tf.train.SessionRunArgs(fetches=fetches, feed_dict={})
        return run_args

    def after_run(self, run_context, run_values):
        loss_hist = self._loss_hist
        outs = run_values.results
        lr = outs.get('lr', 'NA')
        gnorm = outs.get('gnorm', 'NA')
        loss_hist.append(outs['losses'])
        global_step = outs['global_step']

        if self._run_step % self.cfg.verbose == 0:
            avg_loss_str = loss_hist.avg_output()
            logging.info('  name:%s, phase %s, global step:%s, lr:%s, gnorm:%s, loss is:%s', self.name, self._run_phase, global_step, lr,gnorm, avg_loss_str)
        if global_step % self.cfg.save_step == 0 and not self.cfg.use_tf_estimator:
            self.save(global_step)
        if self._run_step % self.cfg.epoch_step == 0 and self._run_phase == 'train':
            avg_loss_str = loss_hist.avg_output()
            logging.info('name:%s, phase %s, epoch:%s, global step:%s, loss is:%s', self.name, self._run_phase, global_step//self.cfg.epoch_step, global_step, avg_loss_str)
            self._loss_hist = LossHist()


    def destroy(self):
        super(TF, self).destroy()
        tf.reset_default_graph()

    def _init_input_features(self):
        return []

    def create_model(self):
        self._graph = tf.Graph()
        self.sess = tf.Session(graph = self._graph)
        self._pred_dict = OrderedDict()
        with self._graph.as_default():
            tf.set_random_seed(self.cfg.seed)
            self._create_graph()
            self.saver = tf.train.Saver(max_to_keep=self.cfg.save_keep, keep_checkpoint_every_n_hours=self.cfg.keep_checkpoint_every_n_hours)
        super(TF, self).create_model()

    def _add_predict(self):
        pass

    def _create_graph(self):
        self._add_plh()
        self._add_main_graph()
        self._add_predict()
        self._add_loss()
        self._add_train()
        self._add_train_nodes()
        self._init_vars()



    def _add_loss(self):
        pass

    def _add_train(self):
        self._var_list = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
        self._train_op, self._gradients, self._global_step, self._lr_node, self._opt, self._gnorm = self._add_train_op(self._loss, self._var_list, clip=self.cfg.gradient_clip)

    def _add_train_nodes(self):
        """
        the name loss is preversed. The fit_epoch function will use key "loss" to fetch the train loss or validation loss,
        if the model have loss of different source, you can add them in the train_nodes and validate_nodes to monitor them.
        For example, the model have loss_1 and loss_2, loss=loss_1+loss_2, you can add these 3 nodes in the validate_nodes.
        :return:
        """
        n_params = int(sum([np.prod(v.shape) for v in tf.trainable_variables()]))
        logging.info('total num of trainable params:%s', n_params)

        train_losses = OrderedDict()
        train_losses['loss'] = self._loss
        self.train_nodes = {'losses': train_losses, 'global_step': self._global_step, 'lr':self._lr_node, 'train_op': self._train_op}
        if self._gnorm is not None:
            self.train_nodes['gnorm'] = self._gnorm

        validate_losses = OrderedDict()
        validate_losses['loss'] = self._loss
        self.validate_nodes = {'losses': validate_losses, 'global_step': self._global_step}

    def _init_vars(self):
        self._var_init = tf.global_variables_initializer()
        self.sess.run(self._var_init)

    def _add_opt(self, loss, var_list, name='train_op', clip=None, lr_node=None, global_step=None, opt=None, opt_name='adam'):
        if global_step is None:
            global_step = tf.train.get_global_step()
            if global_step is None:
                global_step = tf.Variable(0, trainable=False, name='global_step')

        if self.cfg.warmup_steps > 0:
            warmup_lr = tf.to_float(global_step) / tf.to_float(self.cfg.warmup_steps) * self.cfg.lr
        else:
            warmup_lr = 0.0
        if lr_node is None:
            #decaly_lr = tf.train.exponential_decay(learning_rate=self._lr_plh, global_step=global_step-self.cfg.warmup_steps, staircase=False, decay_steps = self.cfg.lr_decay_step, decay_rate=self.cfg.lr_decay_rate, name = 'learning_rate')
            decay_lr = tf.train.cosine_decay(self._lr_plh, global_step=global_step - self.cfg.warmup_steps, decay_steps=self.cfg.lr_decay_step, alpha=self.cfg.min_lr_ratio)
            lr_node = tf.where(global_step < self.cfg.warmup_steps, warmup_lr, decay_lr)
        if opt is None:
            opt = tf.train.AdamOptimizer(learning_rate=lr_node, name=opt_name)
            if self.cfg.use_tpu:
                opt = tf.contrib.tpu.CrossShardOptimizer(opt)
        return opt, lr_node, global_step

    def _add_train_op(self, loss, var_list, name='train_op', clip=None, lr_node=None, global_step=None, opt=None, opt_name='adam'):
        opt, lr_node, global_step = self._add_opt(loss, var_list, name=name, clip=clip, lr_node=lr_node, global_step=global_step, opt=opt, opt_name=opt_name)

        grads = tf.gradients(loss, var_list)
        gnorm = None
        #self._add_summary([loss])
        #self._add_summary([grad for grad, var in gradients if grad is not None], tf.summary.histogram)
        if clip is not None:
            (grads, gnorm) = tf.clip_by_global_norm(grads, clip_norm=clip)
        #if cfg.batch_norm:
        #    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        #    with tf.control_dependencies(update_ops):
        #        self._train_op = opt.apply_gradients(clipped, global_step=self._global_step, name = 'train_op')
        #else:
        train_op = opt.apply_gradients(zip(grads, var_list), global_step=global_step, name=name)
        #self._train_op = opt.minimize(self.loss, global_step=self._global_step, name = 'train_op')
        return train_op, grads, global_step, lr_node, opt, gnorm

    def _add_inputs_plh(self, input_features):
        input_plhs = {}
        for fea in input_features:
            plh = tf.placeholder(fea.dtype, fea.shape, name=fea.name)
            setattr(self, fea.name, plh)
            input_plhs[fea.name] = plh
        return input_plhs

#        if self.cfg.use_tf_estimator:
#            dtypes, shapes = zip(*[[fea.dtype, fea.shape] for fea in self._input_features])
#            self._tf_queue = tf.FIFOQueue(capacity=self.cfg.tf_qsize, dtypes=dtypes, shapes=shapes)
#            self.enqueue_op = self._tf_queue.enqueue(self._input_plhs)
#            self._input_tensors = self._tf_queue.dequeue()
#            for tensor in self._input_tensors:
#                setattr(self, tensor.name, tensor)

    def _add_plh(self):
        self._lr_plh = tf.placeholder(tf.float32, name = "lr_plh" )
        self._training_plh = tf.placeholder(tf.bool, name="training_plh" )
        if self.cfg.dropout is not None:
            self._dropout_plh = tf.placeholder(tf.float32, None, name="dropout_plh" )
        else:
            self._dropout_plh = None
        self._input_plhs = self._add_inputs_plh(self._input_features)

    def _add_emb(self, inputs, size, dim = None, name='emb', embedding = None, trainable=True, scope = 'emb'):
        initializer = tf.contrib.layers.xavier_initializer(uniform=True)
        with tf.variable_scope(scope, initializer = initializer, reuse = tf.AUTO_REUSE):
            if embedding is None:
                embed_var = tf.get_variable(name + '_W', [size, dim], tf.float32, initializer = initializer, trainable = trainable)
            else:
                embed_var = tf.get_variable(name + '_W', initializer = embedding, trainable = trainable)
        embeded = tf.nn.embedding_lookup(embed_var, inputs, name = name)
        return embeded, embed_var


    def save(self, global_step = None):
        super(TF, self).save()
        fpath = self.gen_fname('', 'model.ckpt')
        save_path = self.saver.save(self.sess, fpath, global_step=global_step)
        logging.info("Model saved to file:{}".format(save_path))
        self.batch_reader.save()

    def get_checkpoint_path(self, model_dir=None, global_step=None):
        if model_dir is None:
            model_dir = self.gen_fname('')
        if global_step is None:
            ckpt = tf.train.get_checkpoint_state(model_dir)
            model_path = ckpt.model_checkpoint_path
        else:
            model_path = os.path.join(model_dir, 'model.ckpt-{}'.format(global_step))
        return model_path


    def restore(self, global_step=None, var_list=None, model_dir=None):
        if global_step is None:
            global_step = self.cfg.global_step  # keep it before the restore of cfg
        super(TF, self).restore()
        if self._model is None:
            self.create_model()

        model_path = self.get_checkpoint_path(model_dir, global_step)
        with self.sess.graph.as_default():
            saver = tf.train.Saver(var_list=var_list)
            saver.restore(self.sess, model_path)
            logging.info("Model restored from file:{}".format(model_path))
        if not self.cfg.only_validate and not self.cfg.no_train:
            self.batch_reader.restore()

    def get_feed(self, batch):
        feed = {
                }
        if 'lr' in batch:
            feed[self._lr_plh] = batch['lr']
            feed[self._training_plh] = True
        else:
            feed[self._training_plh] = False

        if 'dropout' in batch:
            feed[self._dropout_plh] = batch['dropout']

        for fea in self._input_features:
            if fea.name in batch:
                plh = getattr(self, fea.name)
                feed[plh] = batch[fea.name]

        return feed

    def run(self, sess, batch, nodes):
        feed = self.get_feed(batch)
        outputs = sess.run(nodes, feed)
        return outputs

    def _get_lr(self, itr):
        return self.cfg.lr

    def pre_run_batch(self, batch, epoch=0, itr=0, global_step=0, is_training=True):
        if is_training:
            batch['lr'] = self._get_lr(itr)
            if self.cfg.dropout is not None:
                batch['dropout'] = self.cfg.dropout
        else:
            if self.cfg.dropout is not None:
                batch['dropout'] = 1.0
        return batch

    def _get_tfrecord_spec(self, input_features):
        record_spec = {}
        for fea in input_features:
            record_spec[fea.name] = tf.FixedLenFeature(fea.shape, fea.dtype)
        return record_spec

    def _get_input_fn(self, x, y, shuffle, data_type):
        record_spec = self._get_tfrecord_spec(self._input_features)

        def _parse_tfrecord(tfrecord):
            examples = tf.parse_single_example(tfrecord, record_spec)
            return examples

        n_batch = None
        if self.cfg.use_tpu:
            fname = self.name + '_' + data_type + '.tfrecords'
            info_fname = self.name + '_' + data_type + '.tfrecords_info'
            record_info = {}
            gsurl = os.path.join(self.cfg.gsurl, os.path.basename(self.gen_fname('')), fname)
            info_gsurl = os.path.join(self.cfg.gsurl, os.path.basename(self.gen_fname('')), info_fname)
            fpath = self.gen_fname('', fname)
            info_fpath = self.gen_fname('', info_fname)
            cmd = 'gsutil -q stat ' + gsurl
            rst = os.system(cmd)
            if rst != 0 or self.cfg.regen_tfrecord:
                if not os.path.exists(fpath) or self.cfg.regen_tfrecord:
                    ds = self._create_dataset(x, y, self.cfg.batch_size, shuffle=shuffle, data_type=data_type)
                    n_batch = tf_util.ds2tfrecord(ds, self._input_features, fpath)
                    record_info['n_batch'] = n_batch
                    logging.info('tf records file generated:%s, total of %s batch', fpath, n_batch)
                    util.dump_json(record_info, info_fpath)
                if not self.cfg.fake_colab:
                    cmd = 'gsutil cp ' + info_fpath + ' ' + info_gsurl
                    rst1 = os.system(cmd)
                    logging.info('file %s copied to %s', info_fpath, info_gsurl)
                    assert rst1 == 0, cmd
                    cmd = 'gsutil cp ' + fpath + ' ' + gsurl
                    rst2 = os.system(cmd)
                    assert rst2 == 0, cmd
                    logging.info('file %s copied to %s', fpath, gsurl)
            else:
                record_info = util.load_json(info_fpath)
                n_batch = record_info['n_batch']

        def _input_fn(params):
            batch_size = params.get('batch_size')
            logging.info('input func batch size is %s', batch_size)
            if not self.cfg.use_tpu:
                ds = self._create_dataset(x, y, batch_size, data_type=data_type, shuffle=shuffle)
            else:
                if not self.cfg.fake_colab:
                    ds = tf.data.TFRecordDataset(gsurl)
                else:
                    ds = tf.data.TFRecordDataset(fpath)
                ds = ds.map(_parse_tfrecord).apply(tf.data.experimental.unbatch())
                if data_type == 'train':
                    ds = ds.cache().repeat()
                    ds = ds.batch(batch_size, drop_remainder=True)
                    ds = ds.prefetch(self.cfg.num_core_per_host * batch_size)
                else:
                    ds = ds.batch(batch_size, drop_remainder=True)
            return ds
        return _input_fn, n_batch

    def _create_dataset(self, x, y, batch_size, data_type, shuffle=False):
        dtypes = {}; shapes = {}
        record_spec = self._get_tfrecord_spec(self._input_features)
        for fea in self._input_features:
            if fea.name in record_spec:
                dtypes[fea.name] = fea.dtype
                shapes[fea.name] = fea.shape

        def _gen():
            for i, batch in enumerate(self.batch_reader(x, batch_size, y, shuffle=shuffle, data_type=data_type)):
                features = {}
                for fea in self._input_features:
                    if fea.name in batch:
                        features[fea.name] = batch[fea.name]
                yield features
        ds = tf.data.Dataset.from_generator(_gen, dtypes, shapes)
        return ds

    def _set_model_fn_inputs(self, features, params):
        for name, fea in features.items():
            setattr(self, name, fea)
            logging.info("feature %s:%s", name, fea)
        plh_features = []
        for fea in self._input_features:
            if fea.name not in features and not self.cfg.use_tpu:
                plh_features.append(fea)
        self._input_plhs = self._add_inputs_plh(plh_features)

    def _metric_fn(self, loss):
        return {
            "loss": tf.metrics.mean(loss),
        }

    def _get_estimator_spec(self, mode, batch_size, hooks=None):
        output_spec = None
        if mode == tf.estimator.ModeKeys.TRAIN:
            output_spec = tf.contrib.tpu.TPUEstimatorSpec(
                mode=mode,
                loss=self._loss,
                train_op=self._train_op,
                training_hooks=hooks,
            )
        elif mode == tf.estimator.ModeKeys.EVAL:
            loss = self._loss
            if self.cfg.use_tpu:
                with tf.colocate_with(loss):
                    loss = tf.contrib.tpu.cross_replica_sum(loss) \
                                 / self.cfg.num_hosts / self.cfg.num_core_per_host
            metric_loss = tf.tile(tf.reshape(loss, [1, 1]), [batch_size, 1])

            output_spec = tf.contrib.tpu.TPUEstimatorSpec(
                mode=mode,
                loss=loss,
                evaluation_hooks=hooks,
                eval_metrics=(self._metric_fn, [metric_loss]),
                )

        return output_spec

    def _get_model_fn(self, ):
        def model_fn(features, labels, mode, params):
            batch_size = params['batch_size']
            logging.info('model func batch_size:%s', batch_size)
            self._set_model_fn_inputs(features, params)

            is_training = (mode == tf.estimator.ModeKeys.TRAIN)
            self._training_plh = tf.constant(is_training)
            if self.cfg.dropout is not None:
                if is_training:
                    self._dropout_plh = tf.constant(self.cfg.dropout)
                else:
                    self._dropout_plh = tf.constant(1.0)
            self._lr_plh = tf.constant(self.cfg.lr)
            self._add_main_graph()
            self._add_loss()
            self._add_train()
            self._add_train_nodes()
            return self._get_estimator_spec(mode, batch_size, hooks=[self])
        return model_fn

    def _get_estimator(self, model_fn, run_config, warm_start_from):
        estimator = tf.contrib.tpu.TPUEstimator(
            use_tpu=self.cfg.use_tpu,
            model_fn=model_fn,
            config=run_config,
            train_batch_size=self.cfg.batch_size,
            eval_batch_size=self.cfg.val_batch_size,
            warm_start_from=warm_start_from)
        return estimator

    def fit_estimator(self, x, y, xV = None, yV = None, save=False, restore=False, xTest=None):
        if self.cfg.fake_colab:
            train_input_fn, n_batch = self._get_input_fn(x, y, shuffle=False, data_type="train")
            val_input_fn, n_batch = self._get_input_fn(xV, yV, shuffle=False, data_type="validate")
            ds = val_input_fn(params={'batch_size':self.cfg.batch_size//self.cfg.num_core_per_host})
            fea_dict = ds.make_one_shot_iterator().get_next()
            with tf.Session() as sess:
                steps = n_batch//self.cfg.batch_size
                try:
                    for i in range(steps):
                        aaa = sess.run(fea_dict)
                except tf.errors.OutOfRangeError as e:
                    logging.error('out of range, n_batch:%s, num:%s', n_batch, num)
                    raise e
                finally:
                    logging.error('fake colab done')


        tpu_cluster_resolver = None
        if self.cfg.use_tpu:
            tpu_cluster_resolver = tf.contrib.cluster_resolver.TPUClusterResolver(
                self.cfg.tpu_name, zone=self.cfg.tpu_zone, project=self.cfg.gcp_project)
            model_dir = os.path.join(self.cfg.gsurl, os.path.basename(self.gen_fname('')))
        else:
            model_dir = self.gen_fname('')

        is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
        run_config = tf.contrib.tpu.RunConfig(
            cluster=tpu_cluster_resolver,
            model_dir=model_dir,
            session_config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True),
            save_checkpoints_steps=self.cfg.save_step,
            save_checkpoints_secs=None,
            keep_checkpoint_max=self.cfg.save_keep,
            tpu_config=tf.contrib.tpu.TPUConfig(
                num_shards=self.cfg.num_core_per_host * self.cfg.num_hosts,
                iterations_per_loop = self.cfg.tpu_loop_iterations,
                per_host_input_for_training=is_per_host))

        model_fn = self._get_model_fn()

        # If TPU is not available, this will fall back to normal Estimator on CPU
        # or GPU.
        # warm start
        warm_start_from = None
        if self.cfg.use_tpu:
            if self.cfg.warm_start_path is not None:
                warm_start_from = tf.estimator.WarmStartSettings(ckpt_to_initialize_from=self.cfg.warm_start_path)
        else:
            if self.cfg.restore:
                checkpoint_path = self.get_checkpoint_path(global_step=self.cfg.global_step)
                warm_start_from = tf.estimator.WarmStartSettings( ckpt_to_initialize_from=checkpoint_path)

        estimator = self._get_estimator(model_fn, run_config, warm_start_from)

        best_val_loss = np.inf; val_loss = None
        for i in range(self.cfg.epochs):
            if not self.cfg.only_validate:
                train_input_fn, n_batch = self._get_input_fn(x, y, shuffle=False, data_type="train")
                if n_batch is not None:
                    steps = n_batch//self.cfg.num_hosts
                else:
                    steps = 1000000000
                self._run_phase = 'train'
                logging.info('run phase:%s, steps:%s', self._run_phase, steps)
                estimator.train(input_fn=train_input_fn, steps=steps)
                logging.info('train epoch %s done', i)
            if xV is not None and not self.cfg.no_validate:
                eval_input_fn, n_batch = self._get_input_fn(xV, yV, shuffle=False, data_type="validate")
                if n_batch is not None:
                    steps = n_batch
                else:
                    steps = 1000000000
                self._run_phase = 'validate'
                logging.info('run phase:%s, steps:%s', self._run_phase, steps)
                val_loss = estimator.evaluate(input_fn=eval_input_fn, steps=steps)['loss']
                logging.info('val loss for epoch %s is %s', i, val_loss)
                if self._should_stop(best_val_loss, val_loss):
                    break
                if val_loss < best_val_loss:
                    best_val_loss = val_loss


    def fit(self, x, y, xV = None, yV = None, save=False, restore=False, xTest=None, no_validate=False, only_validate=False):
        if self.cfg.use_tf_estimator:
            return self.fit_estimator(x, y, xV=xV, yV=yV, save=save, restore=restore, xTest=xTest)
        else:
            return super(TF, self).fit(x, y, xV=xV, yV=yV, save=save, restore=restore, xTest=xTest)

    def fit_batch(self, batch):
        outs = self.run(self.sess, batch, self.train_nodes)
        return outs

    def _update_loss_hist(self, losses, loss_hist):
        for name, loss in losses.items():
            loss_hist[name].append(loss)

    def _get_avg_loss(self, loss_hist):
        avg_loss = OrderedDict()
        for key, v in loss_hist.items():
            avg_loss[key] = np.mean(v)
        return avg_loss

    def _fit_epoch(self, x, y, xV = None, yV = None, epoch=None, xTest = None):
        loss_hist = LossHist()

        if not self.cfg.only_validate:
            itr = 0
            global_step = 0
            for i, batch in enumerate(self.batch_reader(x, self.cfg.batch_size, y, shuffle=True, data_type='train')):
                batch = self.pre_run_batch(batch, epoch, itr, global_step)
                itr += 1
                outs = self.fit_batch(batch)
                lr = outs['lr']
                gnorm = outs.get('gnorm', 'NA')
                loss_hist.append(outs['losses'])
                global_step = outs['global_step']
                if (i+1) % self.cfg.verbose == 0:
                    avg_loss_str = loss_hist.avg_output()
                    logging.info('  name:%s,global step:%s, lr:%s, gnorm:%s, train loss is:%s, totally %s batchs', self.name, global_step, lr,gnorm, avg_loss_str, i+1)
                if (global_step)%self.cfg.save_step == 0:
                    self.save(global_step)
            avg_loss_str = loss_hist.avg_output()
            logging.info('name:%s, epoch:%s, global step:%s,train loss is:%s, totally %s batchs', self.name, epoch, global_step, avg_loss_str, i+1)
            loss = loss_hist.get_avg()['loss']
            if ((epoch+1)%self.cfg.save_epoch) == 0:
                self.save(global_step)
        else:
            global_step = 0
            loss = 0

        if xV is not None and not self.cfg.no_validate:
            val_loss = self.val_epoch(xV, yV, epoch, global_step)
        else:
            val_loss = None
        return loss, val_loss

    def val_epoch(self, xV, yV, epoch, global_step):
        loss_hist = LossHist()
        num_sample = 0
        for i, batch in enumerate(self.batch_reader(xV, self.cfg.val_batch_size, yV, shuffle=False, data_type='validate')):
            batch = self.pre_run_batch(batch, epoch, i, global_step, is_training=False)
            batch_size = batch['batch_size']
            num_sample += batch_size
            outs = self.run(self.sess, batch, self.validate_nodes)
            loss_hist.append(outs['losses'])
        avg_loss_str = loss_hist.avg_output()
        logging.info("epoch:%s, val loss is:%s", epoch, avg_loss_str)
        val_loss = loss_hist.get_avg()['loss']
        return val_loss


    def predict(self, x, do_concat=True, to_list=False):
        preds = defaultdict(list)
        for i, batch in enumerate(self.batch_reader(x, self.cfg.batch_size, shuffle=False, data_type='validate')):
            batch = self.pre_run_batch(batch, 0, i, i, is_training=False)
            batch_pred = self.run(self.sess, batch, self._pred_dict)
            for k, v in batch_pred.items():
                if to_list:
                    preds[k].extend(list(v))
                else:
                    preds[k].append(v)
        if do_concat:
            for k in preds:
                preds[k] = np.concatenate(preds[k],0)
        return preds




