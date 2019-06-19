#!/usr/bin/env python3

"""
@author: xi
@since: 2018-06-09
"""

import tensorflow as tf

import photinia as ph
from . import common


class DDPGAgent(ph.Model):

    def __init__(self,
                 name,
                 input_source_state,
                 input_target_state,
                 input_reward,
                 source_actor,
                 target_actor,
                 source_critic,
                 target_critic,
                 gamma=0.9,
                 tao=0.01,
                 replay_size=10000,
                 optimizer=tf.train.RMSPropOptimizer(1e-4, 0.9, 0.9),
                 reg=ph.reg.L1L2Regularizer(1e-5)):
        """DDPG agent.

        Args:
            name (str): Model name.
            input_source_state: Placeholder of source state.
            input_target_state: Placeholder of target state.
            input_reward: Placeholder of reward.
            source_actor (photinia.Widget): Source actor object.
            target_actor (photinia.Widget): Target actor object.
            source_critic (photinia.Widget): Source critic object.
            target_critic (photinia.Widget): Target critic object.
            gamma (float): Discount factor of reward.
            tao (float):
            replay_size (int): Size of replay memory.
            optimizer: Optimizer to train this model.
            reg (ph.reg.Regularizer): Regularizer.

        """
        self._input_source_state = input_source_state
        self._input_target_state = input_target_state
        self._input_reward = input_reward
        self._source_actor = source_actor
        self._target_actor = target_actor
        self._source_critic = source_critic
        self._target_critic = target_critic
        self._gamma = gamma
        self._tao = tao
        self._replay_size = replay_size
        self._optimizer = optimizer
        self._reg = reg

        self._replay = common.ReplayMemory(replay_size)
        super(DDPGAgent, self).__init__(name)

    def _build(self):
        source_actor = self._source_actor
        target_actor = self._target_actor
        source_critic = self._source_critic
        target_critic = self._target_critic

        #
        # connect source
        input_source_state = self._input_source_state
        source_action = source_actor.setup(input_source_state)
        source_reward = source_critic.setup(input_source_state, source_action)

        #
        # connect target
        input_target_state = self._input_target_state
        target_action = target_actor.setup(input_target_state)
        target_reward = target_critic.setup(input_target_state, target_action)

        #
        # predict
        self._step_predict = ph.Step(
            inputs=input_source_state,
            outputs=source_action
        )

        #
        # train critic
        input_reward = self._input_reward
        y = input_reward + self._gamma * target_reward
        critic_loss = tf.reduce_mean(tf.square(y - source_reward))
        var_list = source_critic.get_trainable_variables()
        if self._reg is not None:
            update = self._optimizer.minimize(critic_loss + self._reg.get_loss(), var_list=var_list)
        else:
            update = self._optimizer.minimize(critic_loss, var_list=var_list)
        self._step_train_critic = ph.Step(
            inputs=(input_source_state, source_action, input_reward, input_target_state),
            outputs=critic_loss,
            updates=update
        )

        #
        # train actor
        var_list = source_actor.get_trainable_variables()
        actor_loss = -tf.reduce_mean(source_reward)
        if self._reg is not None:
            update = self._optimizer.minimize(actor_loss + self._reg.get_loss(), var_list=var_list)
        else:
            update = self._optimizer.minimize(actor_loss, var_list=var_list)
        self._step_train_actor = ph.Step(
            inputs=input_source_state,
            outputs=actor_loss,
            updates=update
        )

        #
        # update target networks
        source_var_list = source_critic.get_trainable_variables() + source_actor.get_trainable_variables()
        target_var_liet = target_critic.get_trainable_variables() + target_actor.get_trainable_variables()
        self._step_update_target = ph.Step(
            updates=tf.group(*[
                tf.assign(v_target, self._tao * v_source + (1.0 - self._tao) * v_target)
                for v_source, v_target in zip(source_var_list, target_var_liet)
            ])
        )

        #
        # init the target networks
        self._step_init_target = ph.Step(
            updates=tf.group(*[
                tf.assign(v_target, v_source)
                for v_source, v_target in zip(source_var_list, target_var_liet)
            ])
        )

    def init(self):
        self._step_init_target()

    def predict(self, state):
        return self._step_predict(state)

    def feedback(self, state, action, reward, state_, done=False):
        self._replay.put(state, action, reward, state_, done)

    def train(self, batch_size):
        state, action, reward, state_ = self._replay.get(batch_size)[:-1]
        critic_loss, = self._step_train_critic(state, action, reward, state_)
        actor_loss, = self._step_train_actor(state)
        self._step_update_target()
        return critic_loss, actor_loss
