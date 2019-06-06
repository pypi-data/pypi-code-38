import time, logging, numpy as np, json
from copy import deepcopy
from collections import namedtuple
from collections import OrderedDict, defaultdict

from .basic_model import BasicModel, InputFeature, LossHist
from .data_reader import create_data_reader

import tensorflow as tf


class TF(BasicModel):
    cfg = deepcopy(BasicModel.cfg)
    cfg.fit_verbose = 30
    cfg.global_step = None
    cfg.batch_reader_cfg = {'process_mode': 'N'}
    cfg.gradient_clip = None
    cfg.batch_reader = 'BatchReader'
    cfg.dropout = None

    def __init__(self, name = 'TF', cfg={}, batch_reader=None):
        super(TF, self).__init__(name, cfg)
        self._input_features = self._init_input_features()
        if batch_reader is None:
            batch_reader = self.cfg.batch_reader

        if isinstance(batch_reader, str):
            self.batch_reader = create_data_reader(batch_reader, 'batch_reader', self.cfg.seed, **self.cfg.batch_reader_cfg)
        else:
            self.batch_reader = batch_reader

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
        super(TF, self).create_model()

    def _create_graph(self):
        self._add_plh()
        self._add_main_graph()
        self._add_loss()
        self._add_train()
        self._add_train_nodes()
        self._init_vars()

    def _add_loss(self):
        pass

    def _add_train(self):
        self._var_list = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
        self._train_op, self._gradients, self._global_step, self._lr_node, self._opt = self._add_train_op(self._loss, self._var_list, clip=self.cfg.gradient_clip)

    def _add_train_nodes(self):
        """
        the name loss is preversed. The fit_epoch function will use key "loss" to fetch the train loss or validation loss,
        if the model have loss of different source, you can add them in the train_nodes and validate_nodes to monitor them.
        For example, the model have loss_1 and loss_2, loss=loss_1+loss_2, you can add these 3 nodes in the validate_nodes.
        :return:
        """
        train_losses = OrderedDict()
        train_losses['loss'] = self._loss
        self.train_nodes = {'losses': train_losses, 'global_step': self._global_step, 'train_op': self._train_op}

        validate_losses = OrderedDict()
        validate_losses['loss'] = self._loss
        self.validate_nodes = {'losses': validate_losses, 'global_step': self._global_step}

    def _init_vars(self):
        self._var_init = tf.global_variables_initializer()
        self.sess.run(self._var_init)

    def _add_train_op(self, loss, var_list, name='train_op', clip=None, lr_node=None, global_step=None, opt=None, opt_name='adam'):
        if global_step is None:
            global_step = tf.Variable(0, trainable=False, name = 'global_step')
        if lr_node is None:
            lr_node = tf.train.exponential_decay(learning_rate=self._lr_plh, global_step=global_step, staircase=False, decay_steps = self.cfg.lr_decay_steps, decay_rate=self.cfg.lr_decay_rate, name = 'learning_rate')
        self._lr_node = lr_node
        if opt is None:
            opt = tf.train.AdamOptimizer(learning_rate=lr_node, name=opt_name)

        grads = tf.gradients(loss, var_list)
        #self._add_summary([loss])
        #self._add_summary([grad for grad, var in gradients if grad is not None], tf.summary.histogram)
        if clip is not None:
            (grads, _) = tf.clip_by_global_norm(grads, clip_norm=clip)
        #if cfg.batch_norm:
        #    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        #    with tf.control_dependencies(update_ops):
        #        self._train_op = opt.apply_gradients(clipped, global_step=self._global_step, name = 'train_op')
        #else:
        train_op = opt.apply_gradients(zip(grads, var_list), global_step=global_step, name=name)
        #self._train_op = opt.minimize(self.loss, global_step=self._global_step, name = 'train_op')
        return train_op, grads, global_step, lr_node, opt

    def _add_inputs_plh(self):
        for fea in self._input_features:
            setattr(self, fea.name, tf.placeholder(fea.dtype, fea.shape, name = fea.name))

    def _add_plh(self):
        self._lr_plh = tf.placeholder(tf.float32, name = "lr_plh" )
        self._training_plh = tf.placeholder(tf.bool, name="training_plh" )
        if self.cfg.dropout is not None:
            self._dropout_plh = tf.placeholder(tf.float32, None, name="dropout_plh" )
        else:
            self._dropout_plh = None
        self._add_inputs_plh()

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
        fpath = self.gen_fname('', 'model')
        with self.sess.graph.as_default():
            saver = tf.train.Saver()
        save_path = saver.save(self.sess, fpath, global_step=global_step)
        logging.info("Model saved to file:{}".format(save_path))

    def restore(self, global_step=None):
        if global_step is None:
            global_step = self.cfg.global_step  # keep it before the restore of cfg
        super(TF, self).restore()
        if self._model is None:
            self.create_model()

        with self.sess.graph.as_default():
            saver = tf.train.Saver()
            fpath = self.gen_fname('')
            if global_step is None:
                ckpt = tf.train.get_checkpoint_state(fpath)
                model_path = ckpt.model_checkpoint_path
            else:
                fpath = self.gen_fname('', 'model')
                model_path = fpath + "-{}".format(global_step)
            saver.restore(self.sess, model_path)
            logging.info("Model restored from file:{}".format(model_path))

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

    def _fit_epoch(self, x, y, xV = None, yV = None, no_validate=False, epoch=None, xTest = None, save_epoch=10000000, only_validate=False):
        loss_hist = LossHist()

        if not only_validate:
            itr = 0
            global_step = 0
            for i, batch in enumerate(self.batch_reader(x, self.cfg.batch_size, y, shuffle=True, data_type='train')):
                batch = self.pre_run_batch(batch, epoch, itr, global_step)
                itr += 1
                outs = self.fit_batch(batch)
                loss_hist.append(outs['losses'])
                global_step = outs['global_step']
                if (i+1) % self.cfg.fit_verbose == 0:
                    avg_loss_str = loss_hist.avg_output()
                    logging.info('  name:%s,global step:%s,train loss is:%s, totally %s batchs', self.name, global_step, avg_loss_str, i+1)
            avg_loss_str = loss_hist.avg_output()
            logging.info('name:%s, epoch:%s, global step:%s,train loss is:%s, totally %s batchs', self.name, epoch, global_step, avg_loss_str, i+1)
            loss = loss_hist.get_avg()['loss']
            if ((epoch+1)%save_epoch) == 0:
                self.save(global_step)
        else:
            global_step = 0
            loss = 0

        if xV is not None and not no_validate:
            loss_hist = LossHist()
            num_sample = 0
            for i, batch in enumerate(self.batch_reader(xV, self.cfg.batch_size, yV, shuffle=False, data_type='validate')):
                batch = self.pre_run_batch(batch, epoch, i, global_step, is_training=False)
                batch_size = batch['batch_size']
                num_sample += batch_size
                outs = self.run(self.sess, batch, self.validate_nodes)
                loss_hist.append(outs['losses'])
            avg_loss_str = loss_hist.avg_output()
            logging.info("epoch:%s, val loss is:%s", epoch, avg_loss_str)
            val_loss = loss_hist.get_avg()['loss']
        else:
            val_loss = None
        return loss, val_loss

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
