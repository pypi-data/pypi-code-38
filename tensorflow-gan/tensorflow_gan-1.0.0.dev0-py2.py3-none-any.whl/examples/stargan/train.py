# coding=utf-8
# Copyright 2019 The TensorFlow GAN Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Trains a StarGAN model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags
import tensorflow as tf
import tensorflow_gan as tfgan

from tensorflow_gan.examples.stargan import data_provider
from tensorflow_gan.examples.stargan import network

# FLAGS for data.
flags.DEFINE_integer('batch_size_stargan', 6, 'The number of images in each batch.')
flags.DEFINE_integer('patch_size_stargan', 128, 'The patch size of images.')

flags.DEFINE_string('train_log_dir', '/tmp/tfgan_logdir/stargan/',
                    'Directory where to write event logs.')

# FLAGS for training hyper-parameters.
flags.DEFINE_float('generator_lr_stargan', 1e-4, 'The generator learning rate.')
flags.DEFINE_float('discriminator_lr_stargan', 1e-4, 'The discriminator learning rate.')
flags.DEFINE_integer('max_number_of_steps_stargan', 1000000,
                     'The maximum number of gradient steps.')
flags.DEFINE_float('adam_beta1_stargan', 0.5, 'Adam Beta 1 for the Adam optimizer.')
flags.DEFINE_float('adam_beta2_stargan', 0.999, 'Adam Beta 2 for the Adam optimizer.')
flags.DEFINE_float('gen_disc_step_ratio_stargan', 0.2,
                   'Generator:Discriminator training step ratio.')

# FLAGS for distributed training.
flags.DEFINE_string('tf_master', '', 'Name of the TensorFlow master.')
flags.DEFINE_integer(
    'ps_replicas_stargan', 0,
    'The number of parameter servers. If the value is 0, then the parameters '
    'are handled locally by the worker.')
flags.DEFINE_integer(
    'task', 0,
    'The Task ID. This value is used when training with multiple workers to '
    'identify each worker.')

FLAGS = flags.FLAGS


def _define_model(images, labels):
  """Create the StarGAN Model.

  Args:
    images: `Tensor` or list of `Tensor` of shape (N, H, W, C).
    labels: `Tensor` or list of `Tensor` of shape (N, num_domains).

  Returns:
    `StarGANModel` namedtuple.
  """

  return tfgan.stargan_model(
      generator_fn=network.generator,
      discriminator_fn=network.discriminator,
      input_data=images,
      input_data_domain_label=labels)


def _get_lr(base_lr):
  """Returns a learning rate `Tensor`.

  Args:
    base_lr: A scalar float `Tensor` or a Python number.  The base learning
      rate.

  Returns:
    A scalar float `Tensor` of learning rate which equals `base_lr` when the
    global training step is less than FLAGS.max_number_of_steps_stargan / 2, afterwards
    it linearly decays to zero.
  """
  global_step = tf.compat.v1.train.get_or_create_global_step()
  lr_constant_steps = FLAGS.max_number_of_steps_stargan // 2

  def _lr_decay():
    return tf.compat.v1.train.polynomial_decay(
        learning_rate=base_lr,
        global_step=(global_step - lr_constant_steps),
        decay_steps=(FLAGS.max_number_of_steps_stargan - lr_constant_steps),
        end_learning_rate=0.0)

  return tf.cond(
      pred=global_step < lr_constant_steps,
      true_fn=lambda: base_lr,
      false_fn=_lr_decay)


def _get_optimizer(gen_lr, dis_lr):
  """Returns generator optimizer and discriminator optimizer.

  Args:
    gen_lr: A scalar float `Tensor` or a Python number.  The Generator learning
      rate.
    dis_lr: A scalar float `Tensor` or a Python number.  The Discriminator
      learning rate.

  Returns:
    A tuple of generator optimizer and discriminator optimizer.
  """
  gen_opt = tf.compat.v1.train.AdamOptimizer(
      gen_lr, beta1=FLAGS.adam_beta1_stargan, beta2=FLAGS.adam_beta2_stargan, use_locking=True)
  dis_opt = tf.compat.v1.train.AdamOptimizer(
      dis_lr, beta1=FLAGS.adam_beta1_stargan, beta2=FLAGS.adam_beta2_stargan, use_locking=True)
  return gen_opt, dis_opt


def _define_train_ops(model, loss):
  """Defines train ops that trains `stargan_model` with `stargan_loss`.

  Args:
    model: A `StarGANModel` namedtuple.
    loss: A `StarGANLoss` namedtuple containing all losses for `stargan_model`.

  Returns:
    A `GANTrainOps` namedtuple.
  """

  gen_lr = _get_lr(FLAGS.generator_lr_stargan)
  dis_lr = _get_lr(FLAGS.discriminator_lr_stargan)
  gen_opt, dis_opt = _get_optimizer(gen_lr, dis_lr)
  train_ops = tfgan.gan_train_ops(
      model,
      loss,
      generator_optimizer=gen_opt,
      discriminator_optimizer=dis_opt,
      summarize_gradients=True,
      colocate_gradients_with_ops=True,
      aggregation_method=tf.AggregationMethod.EXPERIMENTAL_ACCUMULATE_N)

  tf.compat.v1.summary.scalar('generator_lr_stargan', gen_lr)
  tf.compat.v1.summary.scalar('discriminator_lr_stargan', dis_lr)

  return train_ops


def _define_train_step():
  """Get the training step for generator and discriminator for each GAN step.

  Returns:
    GANTrainSteps namedtuple representing the training step configuration.
  """

  if FLAGS.gen_disc_step_ratio_stargan <= 1:
    discriminator_step = int(1 / FLAGS.gen_disc_step_ratio_stargan)
    return tfgan.GANTrainSteps(1, discriminator_step)
  else:
    generator_step = int(FLAGS.gen_disc_step_ratio_stargan)
    return tfgan.GANTrainSteps(generator_step, 1)


def main(_):

  # Create the log_dir if not exist.
  if not tf.io.gfile.exists(FLAGS.train_log_dir):
    tf.io.gfile.makedirs(FLAGS.train_log_dir)

  # Shard the model to different parameter servers.
  with tf.device(tf.compat.v1.train.replica_device_setter(FLAGS.ps_replicas_stargan)):

    # Create the input dataset.
    with tf.compat.v1.name_scope('inputs'), tf.device('/cpu:0'):
      images, labels = data_provider.provide_data('train', FLAGS.batch_size_stargan,
                                                  FLAGS.patch_size_stargan)

    # Define the model.
    with tf.compat.v1.name_scope('model'):
      model = _define_model(images, labels)

    # Add image summary.
    tfgan.eval.add_stargan_image_summaries(
        model, num_images=3 * FLAGS.batch_size_stargan, display_diffs=True)

    # Define the model loss.
    loss = tfgan.stargan_loss(model)

    # Define the train ops.
    with tf.compat.v1.name_scope('train_ops'):
      train_ops = _define_train_ops(model, loss)

    # Define the train steps.
    train_steps = _define_train_step()

    # Define a status message.
    status_message = tf.strings.join([
        'Starting train step: ',
        tf.as_string(tf.compat.v1.train.get_or_create_global_step())
    ],
                                     name='status_message')

    # Train the model.
    tfgan.gan_train(
        train_ops,
        FLAGS.train_log_dir,
        get_hooks_fn=tfgan.get_sequential_train_hooks(train_steps),
        hooks=[
            tf.estimator.StopAtStepHook(num_steps=FLAGS.max_number_of_steps_stargan),
            tf.estimator.LoggingTensorHook([status_message], every_n_iter=10)
        ],
        master=FLAGS.tf_master,
        is_chief=FLAGS.task == 0)


if __name__ == '__main__':
  tf.compat.v1.app.run()
