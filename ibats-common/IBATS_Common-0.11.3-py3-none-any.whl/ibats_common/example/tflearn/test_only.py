#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-5-30 上午8:40
@File    : rnn3_stg.py
@contact : mmmaaaggg@163.com
@desc    : CNN 三分类预测
pip3 install tensorflow sklearn tflearn
"""
import os
import random
import re
from datetime import datetime

import numpy as np
import tensorflow as tf
import tflearn
from ibats_utils.mess import date_2_str, get_last
from sklearn.model_selection import train_test_split
from tflearn import conv_2d, max_pool_2d, local_response_normalization, fully_connected, dropout

from ibats_common import module_root_path
from ibats_common.backend.factor import get_factor
from ibats_common.backend.label import calc_label3
from ibats_common.common import BacktestTradeMode, CalcMode
from ibats_common.example.data import get_trade_date_series, get_delivery_date_series
from ibats_common.strategy import StgBase
from ibats_common.strategy_handler import strategy_handler_factory
from ibats_local_trader.agent.md_agent import *
from ibats_local_trader.agent.td_agent import *

logger = logging.getLogger(__name__)


class AIStg(StgBase):

    def __init__(self, instrument_type, unit=1):
        super().__init__()
        self.unit = unit
        # 模型相关参数
        self.input_size = 38
        self.batch_size = 128
        self.n_step = 60
        self.output_size = 3
        self.n_hidden_units = 10
        self.lr = 0.006
        # 模型训练，及数据集相关参数
        self._model = None
        self._session = None
        self.train_validation_rate = 0.8
        self.n_epoch = 100
        self.xs_train, self.xs_validation, self.ys_train, self.ys_validation = None, None, None, None
        self.label_func_max_rr = 0.0051
        self.label_func_min_rr = -0.0054
        self.max_future = 3
        self.predict_test_random_state = None
        self.retrain_period = 360
        # 其他辅助信息
        self.trade_date_series = get_trade_date_series()
        self.delivery_date_series = get_delivery_date_series(instrument_type)
        self.tensorboard_verbose = 3
        # 模型保存路径相关参数
        self.enable_load_model_if_exist = True
        if self.enable_load_model_if_exist:
            self.base_folder_path = folder_path = os.path.join(module_root_path, f'tf_saves_2019-06-06_08_44_26')
        else:
            datetime_str = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            self.base_folder_path = folder_path = os.path.join(module_root_path, f'tf_saves_{datetime_str}')

        self.model_folder_path = model_folder_path = os.path.join(folder_path, 'model_tfls')
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path, exist_ok=True)
        self.tensorboard_dir = tensorboard_dir = os.path.join(folder_path, f'tensorboard_logs')
        if not os.path.exists(tensorboard_dir):
            os.makedirs(tensorboard_dir)
        self.trade_date_last_train = None

    @property
    def session(self):
        return self.get_session()

    def get_session(self, renew=False, as_default=True, close_last_one_if_renew=True):
        if renew or self._session is None:
            if self.model is None:
                raise ValueError('model 需要先于 session 被创建')
            if close_last_one_if_renew and self._session is not None:
                self._session.close()
            self._session = tf.Session()
            self._session.run(tf.global_variables_initializer())
            # if as_default:
            #     self._session.as_default()
            #     logger.info('default session:%s', self._session.graph)
        return self._session

    @property
    def model(self) -> tflearn.models.DNN:
        return self.get_model()

    def get_model(self, rebuild_model=False) -> tflearn.models.DNN:
        if self._model is None or rebuild_model:
            tf.reset_default_graph()
            self._model = self._build_model()
        return self._model

    def get_factor_array(self, md_df: pd.DataFrame, tail_n=None):
        if tail_n is not None:
            md_df = md_df.tail(tail_n)
        df = md_df[~md_df['close'].isnull()]

        factors = df.fillna(0).to_numpy()
        if self.input_size is None or self.input_size != factors.shape[1]:
            self.input_size = factors.shape[1]
            self.n_hidden_units = self.input_size * 2
            logger.info("set input_size: %d", self.input_size)
            logger.info("set n_hidden_units: %d", self.n_hidden_units)

        return factors, df.index

    def get_x_y(self, factor_df):
        factors, trade_date_index = self.get_factor_array(factor_df)
        price_arr = factors[:, 0]
        self.input_size = factors.shape[1]
        # ys_all = self.calc_y_against_future_data(price_arr, -0.01, 0.01)
        # ys_all = self.calc_y_against_future_data(price_arr, -self.classify_wave_rate, self.classify_wave_rate)
        ys_all = calc_label3(price_arr, self.label_func_min_rr, self.label_func_max_rr,
                             max_future=self.max_future, one_hot=True)
        range_from = self.n_step
        range_to = factors.shape[0]

        xs = np.zeros((range_to - range_from, self.n_step, self.input_size, 1))
        for num, index in enumerate(range(range_from, range_to)):
            xs[num, :, :, :] = factors[(index - self.n_step):index, :, np.newaxis]

        ys = ys_all[range_from:range_to, :]

        return xs, ys, trade_date_index[range_from:range_to]

    def get_batch_xs(self, factors: np.ndarray, index=None):
        """
        取 batch_xs
        :param factors:
        :param index: 样本起始坐标，如果为None，则默认取尾部一组样本
        :return:
        """
        if index is None:
            index = factors.shape[0] - 1

        batch_xs = np.zeros((1, self.n_step, self.input_size, 1))
        batch_xs[0, :, :, :] = factors[(index - self.n_step + 1):(index + 1), :, np.newaxis]

        return batch_xs

    def get_batch_by_random(self, factors: np.ndarray, labels: np.ndarray):
        """
        够在一系列输入输出数据集
        xs： 两条同频率，不同位移的sin曲线
        ys_value： 目标是一条cos曲线
        ys: ys_value 未来涨跌标识
        i_s：X 序列
        """
        xs = np.zeros((self.batch_size, self.n_step, self.input_size))
        ys = np.zeros((self.batch_size, self.output_size))
        # available_batch_size, num = 0, 0
        samples_index = random.sample(range(self.n_step - 1, factors.shape[0] - 1), self.batch_size)
        examples_index_list = []
        for available_batch_size, index in enumerate(samples_index):
            tmp = factors[(index - self.n_step + 1):(index + 1), :]
            if tmp.shape[0] < self.n_step:
                break
            xs[available_batch_size, :, :] = tmp
            ys[available_batch_size, :] = labels[index, :]
            examples_index_list.append(index)
            if available_batch_size + 1 >= self.batch_size:
                available_batch_size += 1
                break

        # returned xs, ys_value and shape (batch, step, input)
        return xs, ys, examples_index_list

    def _build_model(self) -> tflearn.models.DNN:
        # Network building
        net = tflearn.input_data([None, self.n_step, self.input_size, 1])  # input_size=39
        net = tflearn.layers.normalization.batch_normalization(net)
        # layer1
        net = conv_2d(net, 32, 3, activation='relu', name='Conv2D_1')
        net = max_pool_2d(net, 3, strides=2)
        net = local_response_normalization(net)
        # layer2
        net = conv_2d(net, 64, 3, activation='relu', name='Conv2D_2')
        net = max_pool_2d(net, 3, strides=2)
        net = local_response_normalization(net)

        # layer3
        net = conv_2d(net, 128, 3, activation='relu', name='Conv2D_3')
        net = max_pool_2d(net, 3, strides=2)
        net = local_response_normalization(net)

        # layer4
        net = conv_2d(net, 256, 3, activation='relu', name='Conv2D_4')
        net = max_pool_2d(net, 3, strides=2)
        net = local_response_normalization(net)

        net = fully_connected(net, 1024, activation='tanh', name='fc1')
        net = dropout(net, 0.9, name='Dropout1')
        net = fully_connected(net, 1024, activation='tanh', name='fc2')
        net = dropout(net, 0.9, name='Dropout2')
        net = fully_connected(net, self.output_size, activation='softmax')

        net = tflearn.regression(net, optimizer='momentum',
                                 learning_rate=0.001,
                                 loss='categorical_crossentropy')

        # Training
        _model = tflearn.DNN(net, tensorboard_verbose=self.tensorboard_verbose,
                             # checkpoint_path=self.checkpoint_path,
                             tensorboard_dir=self.tensorboard_dir)
        return _model

    def train(self, factor_df, predict_test_random_state):
        xs, ys, _ = self.get_x_y(factor_df)
        trade_date_from, trade_date_to = date_2_str(factor_df.index[0]), date_2_str(factor_df.index[-1])
        # xs_train, xs_validation, ys_train, ys_validation = self.separate_train_validation(xs, ys)
        if self.predict_test_random_state is None:
            random_state = predict_test_random_state
        else:
            random_state = self.predict_test_random_state

        xs_train, xs_validation, ys_train, ys_validation = train_test_split(
            xs, ys, test_size=0.2, random_state=random_state)
        self.xs_train, self.xs_validation, self.ys_train, self.ys_validation = xs_train, xs_validation, ys_train, ys_validation
        sess = self.get_session(renew=True)
        train_acc, val_acc = 0, 0
        with sess.as_default():
            # with tf.Graph().as_default():
            # logger.debug('sess.graph:%s tf.get_default_graph():%s', sess.graph, tf.get_default_graph())
            tflearn.is_training(True)
            logger.debug('xs_train %s, ys_train %s, xs_validation %s, ys_validation %s [%s, %s]',
                         xs_train.shape, ys_train.shape, xs_validation.shape, ys_validation.shape,
                         trade_date_from, trade_date_to)
            for num in range(1, 6):
                logger.info('第 %d 轮训练开始 [%s, %s]', num, trade_date_from, trade_date_to)
                run_id = f'{trade_date_to}_{xs_train.shape[0]}[{predict_test_random_state}]' \
                    f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                self.model.fit(
                    xs_train, ys_train, validation_set=(xs_validation, ys_validation),
                    show_metric=True, batch_size=self.batch_size, n_epoch=self.n_epoch // num,
                    run_id=run_id)

                result = self.model.evaluate(xs_validation, ys_validation, batch_size=self.batch_size)
                logger.info("validation accuracy: %.2f%%" % (result[0] * 100))
                val_acc = result[0]
                break
                # if result[0] > 0.60:
                #     break
                # elif num < 5:
                #     logger.warning('第 %d 轮训练，样本外训练精度不足，继续训练 [%s, %s]', num, trade_date_from, trade_date_to)

            tflearn.is_training(False)

            result = self.model.evaluate(xs_train, ys_train, batch_size=self.batch_size)
            # logger.info("train accuracy: %.2f%%" % (result[0] * 100))
            train_acc = result[0]

        self.trade_date_last_train = trade_date_to
        return self.model, (train_acc, val_acc)

    def save_model(self, trade_date):
        """
        将模型导出到文件
        :param trade_date:
        :return:
        """
        folder_path = os.path.join(self.model_folder_path, date_2_str(trade_date))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(
            folder_path,
            f"model_{int(self.label_func_min_rr * 10000)}_{int(self.label_func_max_rr * 10000)}.tfl")
        self.model.save(file_path)
        logger.info("模型训练截止日期： %s 保存到: %s", self.trade_date_last_train, file_path)
        return file_path

    def load_model_if_exist(self, trade_date):
        """
        将模型导出到文件
        目录结构：
        tf_saves_2019-06-05_16_21_39
          *   model_tfls
          *       *   2012-12-31
          *       *       *   checkpoint
          *       *       *   model_-54_51.tfl.data-00000-of-00001
          *       *       *   model_-54_51.tfl.index
          *       *       *   model_-54_51.tfl.meta
          *       *   2013-02-28
          *       *       *   checkpoint
          *       *       *   model_-54_51.tfl.data-00000-of-00001
          *       *       *   model_-54_51.tfl.index
          *       *       *   model_-54_51.tfl.meta
          *   tensorboard_logs
          *       *   2012-12-31_496[1]_20190605_184316
          *       *       *   events.out.tfevents.1559731396.mg-ubuntu64        datetime_str = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        self.base_folder_path = folder_path = os.path.join(module_root_path, f'tf_saves_{datetime_str}')

          *       *   2013-02-28_496[1]_20190605_184716
          *       *       *   events.out.tfevents.1559731396.mg-ubuntu64
        :param trade_date:
        :return:
        """
        if self.enable_load_model_if_exist:
            # 获取小于等于当期交易日的最大的一个交易日对应的文件名
            # 获取全部文件名
            pattern = re.compile(r'model_[-]?\d+_\d+.tfl')
            date_file_path_pair_list, model_name_set = [], set()
            for folder_name in os.listdir(self.model_folder_path):
                folder_path = os.path.join(self.model_folder_path, folder_name)
                if os.path.isdir(folder_path):
                    try:
                        key = str_2_date(folder_name)
                        for file_name in os.listdir(folder_path):
                            # 对下列有效文件名，匹配结果："model_-54_51.tfl"
                            # model_-54_51.tfl.data-00000-of-00001
                            # model_-54_51.tfl.index
                            # model_-54_51.tfl.meta
                            m = pattern.search(file_name)
                            if m is None:
                                continue
                            model_name = m.group()
                            if model_name in model_name_set:
                                continue
                            model_name_set.add(model_name)
                            file_path = os.path.join(folder_path, model_name)
                            date_file_path_pair_list.append([key, file_path])
                    except:
                        pass
            # 按日期排序
            date_file_path_pair_list.sort(key=lambda x: x[0])
            # 获取小于等于当期交易日的最大的一个交易日对应的文件名
            # file_path = get_last(date_file_path_pair_list, lambda x: x[0] <= trade_date, lambda x: x[1])
            trade_date = str_2_date(trade_date)
            key, folder_path = get_last(date_file_path_pair_list, lambda x: x[0] <= trade_date)
            if folder_path is not None:
                model = self.model  # 这句话是必须的，需要实现建立模型才可以加载
                model.load(folder_path)
                self.trade_date_last_train = key
                logger.info("load from path: %s", folder_path)
                return True

        return False

    def predict_test(self, factor_df):
        logger.info('开始预测')
        # sess = self.session
        if self.xs_train is None:
            xs, ys, _ = self.get_x_y(factor_df)
            xs_train, xs_validation, ys_train, ys_validation = train_test_split(xs, ys, test_size=0.2, random_state=1)
            self.xs_train, self.xs_validation, self.ys_train, self.ys_validation = xs_train, xs_validation, ys_train, ys_validation

        with self.session.as_default() as sess:
            # logger.info('sess.graph:%s', sess.graph)
            # logger.info('tf.get_default_graph():%s', tf.get_default_graph())
            # logger.info("批量预测")
            # result = self.model.evaluate(self.xs_validation, self.ys_validation, batch_size=self.batch_size)
            # logger.info("accuracy: %.2f%%" % (result[0] * 100))

            logger.info("批量预测2")
            real_ys = np.argmax(self.ys_validation, axis=1)
            # pred_ys = np.argmax(self.model.predict_label(self.xs_validation), axis=1) 与 evaluate 结果刚好相反
            # 因此不使用 predict_label 函数
            pred_ys = np.argmax(self.model.predict(self.xs_validation), axis=1)
            logger.info("accuracy: %.2f%%" % (sum(pred_ys == real_ys) / len(pred_ys) * 100))
            # logger.info("pred/real: \n%s\n%s", pred_ys, real_ys)

            logger.info("独立样本预测(predict_latest)")
            pred_ys = []
            for idx, y in enumerate(self.ys_validation):
                x = self.xs_validation[idx:idx + 1, :, :]
                pred_y = self.model.predict(x)
                pred_ys.extend(np.argmax(pred_y, axis=1))

            pred_ys = np.array(pred_ys)
            logger.info("accuracy: %.2f%%" % (sum(pred_ys == real_ys) / len(pred_ys) * 100))
            # logger.info("pred: \n%s\n%s", pred_ys, real_ys)

    def predict_latest(self, md_df):
        """
        计算最新一个 X，返回分类结果
        二分类，返回 0 未知 / 1 下跌 / 2 上涨
        三分类，返回 0 震荡 / 1 下跌 / 2 上涨
        :param md_df:
        :return:
        """
        factors, _ = self.get_factor_array(md_df, tail_n=self.n_step)
        x = self.get_batch_xs(factors)
        pred_y = np.argmax(self.model.predict(x), axis=1)[-1]
        # is_buy, is_sell = pred_mark == 1, pred_mark == 0
        # return is_buy, is_sell
        return pred_y

    def on_prepare_min1(self, md_df, context):
        if md_df is None:
            return
        logger.debug('%s %s', md_df['trade_date'].iloc[-1], md_df.shape)
        df = md_df.set_index('trade_date').drop('instrument_type', axis=1)
        df.index = pd.DatetimeIndex(df.index)
        factor_df = get_factor(df, close_key='close',
                               trade_date_series=self.trade_date_series,
                               delivery_date_series=self.delivery_date_series)

        self.load_train_test(factor_df, enable_load_model=self.enable_load_model_if_exist)

    def load_train_test(self, factor_df, enable_load_model, rebuild_model=False, enable_train_if_load_not_suss=True,
                        enable_train_even_load_succ=False, enable_test=True):
        if rebuild_model:
            self.get_model(rebuild_model=True)

        trade_date = factor_df.index[-1]
        # 加载模型
        if enable_load_model:
            is_load = self.load_model_if_exist(trade_date)
        else:
            is_load = False

        if enable_train_even_load_succ or (enable_train_if_load_not_suss and not is_load):
            num = 0
            while True:
                num += 1
                # 训练模型
                _, (train_acc, val_acc) = self.train(factor_df, num)
                # if val_acc < 0.6:
                #     logger.warning('第 %d 次训练，训练结果不及预期，重新采样训练', num)
                # elif train_acc - val_acc > 0.15 and val_acc < 0.75:
                #     logger.warning('第 %d 次训练，train_acc=%.2f%%, val_acc=%.2f%% 相差大于 15%% 且验证集正确率小于75%%，重新采样训练',
                #                    num, train_acc * 100, val_acc * 100)
                # else:
                break

            self.save_model(trade_date)
            self.trade_date_last_train = trade_date

        if enable_test:
            self.predict_test(factor_df)

    def on_min1(self, md_df, context):
        # logger.debug('%s %s', md_df['trade_date'].iloc[-1], md_df.shape)
        # # 数据整理
        # df = md_df.set_index('trade_date').drop('instrument_type', axis=1)
        # df.index = pd.DatetimeIndex(df.index)
        # df = get_factor(df, close_key='close',
        #                 trade_date_series=self.trade_date_series,
        #                 delivery_date_series=self.delivery_date_series)
        # # 获取最新jiaoyhiriq
        # # trade_date = md_df['trade_date'].iloc[-1]
        # # trade_date = df.index[-1]
        # # days_after_last_train = (trade_date - self.trade_date_last_train).days
        # # if days_after_last_train >= self.retrain_period:
        # #     # 重新训练
        # #     logger.info('当前日期 %s 距离上一次训练 %s 已经过去 %d 天',
        # #                 trade_date, self.trade_date_last_train, days_after_last_train)
        # #     self.load_train_test(df, rebuild_model=True, enable_load_model=False, enable_train=True)
        #
        # # 预测
        # pred_mark = self.predict_latest(df)
        # is_holding, is_buy, is_sell = pred_mark == 0, pred_mark == 1, pred_mark == 2
        # # logger.info('%s is_buy=%s, is_sell=%s', trade_date, str(is_buy), str(is_sell))
        # close = md_df['close'].iloc[-1]
        # instrument_id = context[ContextKey.instrument_id_list][0]
        # if is_buy:  # is_buy
        #     position_date_pos_info_dic = self.get_position(instrument_id)
        #     no_target_position = True
        #     if position_date_pos_info_dic is not None:
        #         for position_date, pos_info in position_date_pos_info_dic.items():
        #             direction = pos_info.direction
        #             if direction == Direction.Short:
        #                 self.close_short(instrument_id, close, pos_info.position)
        #             elif direction == Direction.Long:
        #                 no_target_position = False
        #     if no_target_position:
        #         self.open_long(instrument_id, close, self.unit)
        #     else:
        #         logger.debug("%s %s     %.2f holding", self.trade_agent.curr_timestamp, instrument_id, close)
        #
        # if is_sell:  # is_sell
        #     position_date_pos_info_dic = self.get_position(instrument_id)
        #     no_holding_target_position = True
        #     if position_date_pos_info_dic is not None:
        #         for position_date, pos_info in position_date_pos_info_dic.items():
        #             direction = pos_info.direction
        #             if direction == Direction.Long:
        #                 self.close_long(instrument_id, close, pos_info.position)
        #             elif direction == Direction.Short:
        #                 no_holding_target_position = False
        #     if no_holding_target_position:
        #         self.open_short(instrument_id, close, self.unit)
        #     else:
        #         logger.debug("%s %s     %.2f holding", self.trade_agent.curr_timestamp, instrument_id, close)
        #
        # if is_holding:
        #     logger.debug("%s %s * * %.2f holding", self.trade_agent.curr_timestamp, instrument_id, close)
        pass

    def on_min1_release(self, md_df):
        # logger.debug('%s %s', md_df['trade_date'].iloc[-1], md_df.shape)
        # 建立验证数据集
        df = md_df.set_index('trade_date').drop('instrument_type', axis=1)
        trade_date_list = list(df.index)
        df.index = pd.DatetimeIndex(trade_date_list)
        factor_df = get_factor(df, close_key='close',
                               trade_date_series=self.trade_date_series,
                               delivery_date_series=self.delivery_date_series)
        xs, ys, trade_date_index = self.get_x_y(factor_df)
        is_4_validation = (factor_df.index >= self.trade_date_last_train)[:len(xs)]
        xs, ys = xs[is_4_validation, :, :, :], ys[is_4_validation, :]
        trade_date_list = trade_date_index[is_4_validation]
        close_df = df.loc[trade_date_list, 'close']
        # 预测结果
        logger.info("检验预测结果(predict_latest)")
        real_ys, pred_ys = np.argmax(ys, axis=1), []
        for idx, y in enumerate(ys):
            x = xs[idx:idx + 1, :, :, :]
            pred_y = self.model.predict(x)
            pred_ys.extend(np.argmax(pred_y, axis=1))

        pred_ys = np.array(pred_ys)
        # 分析成功率
        # 累计平均成功率
        logger.info("accuracy: %.2f%%" % (sum(pred_ys == real_ys) / len(pred_ys) * 100))
        is_fit_arr = pred_ys == real_ys
        accuracy_list, fit_sum = [], 0
        for tot_count, (is_fit, trade_date) in enumerate(zip(is_fit_arr, trade_date_list), start=1):
            if is_fit:
                fit_sum += 1
            accuracy_list.append(fit_sum/tot_count)

        accuracy_df = pd.DataFrame({'accuracy': accuracy_list}, index=trade_date_list)
        show_accuracy(accuracy_df, close_df)
        # 移动平均成功率
        accuracy_list, win_size = [], 60
        for idx in range(win_size, len(is_fit_arr)):
            accuracy_list.append(sum(is_fit_arr[idx-win_size:idx]/win_size))

        close2_df = close_df.iloc[win_size:]
        accuracy_df = pd.DataFrame({'accuracy': accuracy_list}, index=close2_df.index)
        show_accuracy(accuracy_df, close2_df)


def show_accuracy(accuracy_df, close_df):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    l1 = ax.plot(accuracy_df, color='r', label='accuracy')
    ax2 = ax.twinx()
    l2 = ax2.plot(close_df, label='base_line')
    lns = l1 + l2
    plt.legend(lns, [_.get_label() for _ in lns], loc=0)
    plt.suptitle(f'累计平均准确率')
    plt.show()


def _test_use(is_plot):
    from ibats_common import module_root_path
    import os
    instrument_type = 'RB'
    # 参数设置
    run_mode = RunMode.Backtest_FixPercent
    calc_mode = CalcMode.Normal
    strategy_params = {'instrument_type': instrument_type, 'unit': 1}
    md_agent_params_list = [{
        'md_period': PeriodType.Min1,
        'instrument_id_list': [instrument_type],
        'datetime_key': 'trade_date',
        'init_md_date_from': '1995-1-1',  # 行情初始化加载历史数据，供策略分析预加载使用
        'init_md_date_to': '2013-1-1',
        # 'C:\GitHub\IBATS_Common\ibats_common\example\ru_price2.csv'
        'file_path': os.path.abspath(os.path.join(module_root_path, 'example', 'data', f'{instrument_type}.csv')),
        'symbol_key': 'instrument_type',
    }]
    if run_mode == RunMode.Realtime:
        trade_agent_params = {
        }
        strategy_handler_param = {
        }
    elif run_mode == RunMode.Backtest:
        trade_agent_params = {
            'trade_mode': BacktestTradeMode.Order_2_Deal,
            'init_cash': 10000,
            "calc_mode": calc_mode,
        }
        strategy_handler_param = {
            'date_from': '2013-1-1',  # 策略回测历史数据，回测指定时间段的历史行情
            'date_to': '2018-10-18',
        }
    else:
        trade_agent_params = {
            'trade_mode': BacktestTradeMode.Order_2_Deal,
            "calc_mode": calc_mode,
        }
        strategy_handler_param = {
            'date_from': '2013-1-1',  # 策略回测历史数据，回测指定时间段的历史行情
            'date_to': '2018-10-18',
        }
    # 初始化策略处理器
    stghandler = strategy_handler_factory(
        stg_class=AIStg,
        strategy_params=strategy_params,
        md_agent_params_list=md_agent_params_list,
        exchange_name=ExchangeName.LocalFile,
        run_mode=run_mode,
        trade_agent_params=trade_agent_params,
        strategy_handler_param=strategy_handler_param,
    )
    stghandler.start()
    time.sleep(10)
    stghandler.keep_running = False
    stghandler.join()
    stg_run_id = stghandler.stg_run_id
    logging.info("执行结束 stg_run_id = %d", stg_run_id)

    if is_plot:
        from ibats_common.analysis.summary import summary_stg_2_docx
        from ibats_utils.mess import open_file_with_system_app
        file_path = summary_stg_2_docx(stg_run_id)
        open_file_with_system_app(file_path)

    return stg_run_id


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG, format=config.LOG_FORMAT)
    _test_use(is_plot=True)
