from __future__ import print_function
from __future__ import unicode_literals
import sys
import time
import os
import io

import six
import torch
from torch.utils.data import dataloader as torch_dataloader
from tensorboardX import SummaryWriter



if six.PY2:
    time.perf_counter = time.time

GREEN_STR = '\033[38;5;2m%s\033[0m'
RED_STR = '\033[38;5;1m%s\033[0m'
INFO_TEMPLATE = '\033[38;5;2mINFO: %s\033[0m'
WARN_TEMPLATE = '\033[38;5;1mWARNING: %s\033[0m'


class BuiltinProgressInfo:
    MODE_INFO = GREEN_STR % '[{mode_str_}]'
    DTS_POSITION_INFO = '{batches_done_in_epoch_}/{batches_in_epoch_} @{epoch}'
    TIME_INFO = 'time: {comp_time_:.3f} - data: {data_time_:.3f} - ETA: {eta_:.0f}'
    SPEED_INFO = 'e/s: {examples_per_sec_:.1f}'
    LOSS_INFO = 'loss: {loss:.3f}'

class MetricPoint(object):

    def __init__(self, value, metadata=None):
        self.value = value
        self.timestamp = time.time()
        self.metadata = metadata


class MetricHistory(object):

    def __init__(self, name):
        self.name = name
        self.history = []
        self.num_written_to_summary = 0

    def _add_metric_point(self, metric_point):
        if isinstance(metric_point, MetricPoint):
            self.history.append(metric_point)
            return metric_point
        elif isinstance(metric_point, (six.integer_types, float)):
            return self._add_metric_point(MetricPoint(metric_point))
        else:
            raise ValueError("Invalid metric point.")

    def add_metric_point(self, metric_point):
        return self._add_metric_point(metric_point)

    def get_last_value(self):
        if self.history:
            return self.history[0].value
        else:
            return None

    def get_running_value(self):
        return self.get_last_value()

    def get_aggregated_value(self,
                             aggregator,
                             metric_point_filter=lambda x: True):
        return aggregator(filter(metric_point_filter, self.history))

    def clear(self):
        self.history = []
        self.num_written_to_summary = 0

    def _write_pending_to_summary_writer(self, summary_writer):
        while self.num_written_to_summary < len(self.history):
            self._write_to_summary_writer(summary_writer,
                                          metric_point=self.history[self.num_written_to_summary],
                                          iteration=self.num_written_to_summary)
            self.num_written_to_summary += 1

    def _write_to_summary_writer(self, summary_writer, metric_point, iteration):
        return


class ScalarMetricHistory(MetricHistory):

    def __init__(self, name, smoothing=0.95):
        super(ScalarMetricHistory, self).__init__(name)
        self.running_value = None
        self.smoothing = smoothing

    def get_running_value(self):
        return self.running_value

    def add_metric_point(self, metric_point):
        metric_point = self._add_metric_point(metric_point)
        if not self.running_value:
            self.running_value = metric_point.value
        self.running_value = self.smoothing * self.running_value + (
            1.0 - self.smoothing) * metric_point.value

    def get_avg(self, metric_point_filter=lambda x: True):
        return self.get_aggregated_value(
            aggregator=lambda x: sum(x) / float(len(x)),
            metric_point_filter=metric_point_filter)

    def _write_to_summary_writer(self, summary_writer, metric_point, iteration):
        if summary_writer is None:
            return
        summary_writer.add_scalar(tag=self.name,
                                  scalar_value=metric_point.value,
                                  global_step=iteration,
                                  walltime=metric_point.timestamp)



class TrainerState(object):

    def __init__(self):
        # State variables automatically populated by the STrainer

        # Output of the last update_fn.
        self.output = None
        # Whether we are training the model now, otherwise evaluating.
        self.is_training = None
        # Device on which the operation was requested.
        self.device = None

        # To be defined by the user! Ideally should subclass TrainerState.
        self.loss = float('nan')

        # Current train/eval evaluators, may be only partially finished.
        self.train_iterator = None
        self.eval_iterator = None

        # Position in training (epoch + batch in epoch).
        self.epoch = None
        self.batches_done_in_epoch_ = None

        # This will be only available if provided by user or if supported data loader was used.
        self.batches_in_epoch_ = float('nan')
        self.examples_in_batch_ = float('nan')

        # Perf metrics.
        self.comp_time_ = ScalarMetricHistory('comp_time')
        self.data_time_ = ScalarMetricHistory('data_time')
        self.batches_per_sec_ = None
        self.examples_per_sec_ = None
        self.eta_ = None

    def get_state_dict(self):
        res = {}
        for k, v in six.iteritems(self.__dict__):
            try:
                torch.save(v, io.BytesIO())
            except Exception:
                print(WARN_TEMPLATE % ("Variable \"%s\" is not save-able." % k))
                continue
            res[k] = v
        return res

    def set_state_dict(self, state_dict):
        for k, v in six.iteritems(state_dict):
            setattr(self, k, v)


    def get_info_dict(self):
        info = {
            'mode_str_': "EVAL" if not self.is_training else "TRAIN"
        }  # hack because of lack of fstring...
        for k, v in six.iteritems(self.__dict__):
            if isinstance(v, (float, six.integer_types, six.string_types)):
                info[k] = v
            elif isinstance(v, MetricHistory):
                info[k] = v.get_running_value()
            else:
                pass
        return info

    def add_scalar_data_point(self, name, scalar_value, smoothing=0.95):
        if not hasattr(self, name) or not isinstance(getattr(self, name), ScalarMetricHistory):
            setattr(self, name, ScalarMetricHistory(name=name, smoothing=smoothing))
        getattr(self, name).add_metric_point(scalar_value)

    def _write_pending_metrics_to_summary_writer(self, summary_writer):
        for v in self.__dict__.values():
            if isinstance(v, MetricHistory):
                v._write_pending_to_summary_writer(summary_writer)


DEFAULT_INFO_STRING_COMPONENTS = (BuiltinProgressInfo.MODE_INFO,
                                  BuiltinProgressInfo.DTS_POSITION_INFO,
                                  BuiltinProgressInfo.TIME_INFO,
                                  BuiltinProgressInfo.SPEED_INFO,
                                  BuiltinProgressInfo.LOSS_INFO)


class STrainer(object):

    def __init__(self,
                 update_fn,
                 modules=None,
                 events=None,
                 saver_config=None,
                 lr_scheduling_config=None,
                 info_string_components=DEFAULT_INFO_STRING_COMPONENTS,
                 state_cls=TrainerState,
                 collect_perf_metrics=True,
                 tensorboard_log_dir=None,
                 summary_writer_kwargs=dict(flush_secs=11),
                 ):
        assert six.get_function_code(
            update_fn
        ).co_argcount == 2, "update_fn must take exactly 2 arguments (trainer_instance, batch) and return outputs"
        self.update_fn = update_fn

        assert issubclass(state_cls, TrainerState)
        self.state = state_cls()

        self.modules = modules
        self.events = events or []
        assert saver_config is None, 'not supported yet'
        self.saver_config = saver_config
        assert lr_scheduling_config is None, 'not supported yet'
        self.lr_scheduling_config = lr_scheduling_config
        self.info_string_components = info_string_components
        self.collect_perf_metrics = collect_perf_metrics
        self.tensorboard_log_dir = os.path.abspath(os.path.expanduser(tensorboard_log_dir)) if tensorboard_log_dir else None
        if self.tensorboard_log_dir is not None:
            if not os.path.exists(self.tensorboard_log_dir):
                os.mkdir(self.tensorboard_log_dir)
            self.summary_writer = SummaryWriter(tensorboard_log_dir, **summary_writer_kwargs)
            print(INFO_TEMPLATE % "SummaryWriter (TensorboardX) will log to: %s" % self.tensorboard_log_dir)
            print(INFO_TEMPLATE % "To Start Tensorboard: tensorboard --logdir=%s" % self.tensorboard_log_dir)
            for i, model in enumerate(self.modules if self.modules else []):
                try:
                    self.summary_writer.add_graph(model)
                except:
                    print(WARN_TEMPLATE % "Could not save module at position %d to the tensorboard graph (not critical)" % i)
                    import traceback
                    print(traceback.format_exc())
        else:
            print(INFO_TEMPLATE % "tensorboard_log_dir not provided, SummaryWriter (for TensorboardX) not configured.")
            self.summary_writer = None

    def display_scalar_metric(self, name, precision='.3f'):
        self.info_string_components += ('%s: {%s:%s}' % (name, name, precision),)


    def _main_loop(self,
                   steps=None,
                   allow_switch_mode=True,
                   device="cpu",
                   info_string=None):
        """Trains for 1 epoch if steps is None. Otherwise performs specified number of steps."""
        assert steps is None or steps >= 1, "Invalid steps, must be None or greater than 0."
        if allow_switch_mode:  # try to set all the modules to the correct trainable state
            if self.modules is not None:
                map(lambda x: x.train(self.state.is_training), self.modules)
            else:
                print(
                    WARN_TEMPLATE %
                    "Could not set the modules to the required training mode because they were not provided, assuming already in the correct mode"
                )

        if info_string is None:
            info_string = ' | '.join(self.info_string_components)

        def maybe_synchronize_cuda():
            if self.collect_perf_metrics and device == 'gpu':
                torch.cuda.synchronize()

        maybe_synchronize_cuda()
        t_fetch = time.perf_counter()
        steps_done_here = 0
        dts_iterator = self.state.train_iterator if self.state.is_training else self.state.eval_iterator
        force_quit = False
        for batch in dts_iterator:

            maybe_synchronize_cuda()
            t_start = time.perf_counter()
            # --------------------------- MAIN STEP ------------------------------------
            self.state.output = self.update_fn(self, batch)
            maybe_synchronize_cuda()
            t_end = time.perf_counter()
            # --------------------------------------------------------------------------

            # Update built-in state variables.
            self.state.batches_done_in_epoch_ += 1
            if self.collect_perf_metrics:
                self.state.comp_time_.add_metric_point(t_end - t_start)
                self.state.data_time_.add_metric_point(t_start - t_fetch)
                self.state.batches_per_sec_ = 1. / (
                    self.state.comp_time_.get_running_value() +
                    self.state.data_time_.get_running_value())
                self.state.examples_per_sec_ = self.state.batches_per_sec_ * self.state.examples_in_batch_
                self.state.eta_ = (self.state.batches_in_epoch_ -
                                   self.state.batches_done_in_epoch_
                                  ) / self.state.batches_per_sec_

            # Call events.
            for event in self.events:
                if event(self):
                    force_quit = True

            # Render and print the info.
            formatted_info_string = info_string.format(
                **self.state.get_info_dict())
            sys.stdout.write('\r' + formatted_info_string)
            sys.stdout.flush()
            sys.stdout.flush()

            # Write to summaries for tensorboard
            if self.summary_writer is not None:
                self.state._write_pending_metrics_to_summary_writer(self.summary_writer)

            steps_done_here += 1

            # Handle early exit.
            if force_quit or (steps is not None and steps <= steps_done_here):
                print()
                print(INFO_TEMPLATE %
                      ("Early left the training loop at epoch %d, batch %d" %
                       (self.state.epoch, self.state.batches_done_in_epoch_)))
                break

            t_fetch = t_end
        else:
            # Invalidate the current dts_iterator in the state if fully finished the iteration, also bump the epoch.
            if self.state.is_training:
                self.state.train_iterator = None
                self.state.epoch += 1
            else:
                self.state.eval_iterator = None
        print()

    def _run_main_loop(self,
                       dts_loader,
                       is_training,
                       device='cpu',
                       steps=None,
                       allow_switch_training_mode=True,
                       continue_training=False):
        self.state.is_training = is_training
        if is_training:
            if continue_training:
                if self.state.train_iterator is None:
                    print(
                        INFO_TEMPLATE %
                        "The train dataset has been already fully iterated, not possible to continue."
                    )
                    if dts_loader is not None:
                        print(INFO_TEMPLATE % "Starting new epoch to continue.")
                        return self.train(
                            dts_loader,
                            device=device,
                            steps=steps,
                            allow_switch_training_mode=True)
                    else:
                        print(INFO_TEMPLATE %
                              "No dts_loader provided, cannot start new epoch.")
                        return
            else:
                self.state.train_iterator = iter(dts_loader)
                self.state.epoch = 1 if self.state.epoch is None else self.state.epoch
                self.state.batches_done_in_epoch_ = 0
        else:
            assert not continue_training
            self.state.eval_iterator = iter(dts_loader)
            self.state.batches_done_in_epoch_ = 0
        self.state.device = device
        if isinstance(dts_loader, torch_dataloader.DataLoader):
            self.state.batches_in_epoch_ = len(dts_loader)
            self.state.examples_in_batch_ = dts_loader.batch_size
        elif isinstance(dts_loader, torch_dataloader._DataLoaderIter):
            self.state.batches_in_epoch_ = len(dts_loader)
            self.state.examples_in_batch_ = len(
                dts_loader.dataset) / len(dts_loader)
        elif hasattr(dts_loader, '__len__'):
            self.state.batches_in_epoch_ = len(dts_loader)
            print(
                WARN_TEMPLATE %
                "Could not extract the dataset size info (batch_size), use torch.utils.data.dataloader.DataLoader."
            )
        else:
            print(
                WARN_TEMPLATE %
                "Could not extract the dataset size info (batch_size and num_batches), use torch.utils.data.dataloader.DataLoader."
            )
        return self._main_loop(
            steps=steps,
            device=device,
            allow_switch_mode=allow_switch_training_mode)

    def train(self,
              dts_loader,
              device='cpu',
              steps=None,
              allow_switch_training_mode=True):
        return self._run_main_loop(
            dts_loader,
            is_training=True,
            device=device,
            steps=steps,
            allow_switch_training_mode=allow_switch_training_mode)

    def continue_train(self,
                       device='cpu',
                       steps=None,
                       allow_switch_training_mode=False):
        return self._run_main_loop(
            None,
            is_training=True,
            device=device,
            steps=steps,
            allow_switch_training_mode=allow_switch_training_mode,
            continue_training=True)

    def evaluate(self,
                 dts_loader,
                 device='cpu',
                 steps=None,
                 allow_switch_training_mode=True):
        return self._run_main_loop(
            dts_loader,
            is_training=False,
            device=device,
            steps=steps,
            allow_switch_training_mode=allow_switch_training_mode)

    def _get_state_dict(self):
        return dict(
            trainer_state_dict=self.state.get_state_dict(),
            state_dicts=[m.state_dict() for m in (self.modules or [])],
        )

    def _set_state_dict(self, state_dict):
        self.state.set_state_dict(state_dict['trainer_state_dict'])
        for m, s in zip(self.modules or [], state_dict['state_dicts']):
            m.load_state_dict(s)

    def save(self, save_dir, step=1):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        p = os.path.join(save_dir, 'model-%d.ckpt' % step)
        torch.save(self._get_state_dict(), p)
        print(INFO_TEMPLATE % ("Model saved at %s." % p))

    def restore(self, save_dir, step=1):
        p = os.path.join(save_dir, 'model-%d.ckpt' % step)
        if not os.path.exists(p):
            print(WARN_TEMPLATE % ("Could not find a checkpoint at %s, skipping restore." % p))
            return
        else:
            self._set_state_dict(torch.load(p))
            print(INFO_TEMPLATE % ("Model restored from checkpoint at %s." % p))



class BaseEvent:

    def __init__(self):
        self.func = None

    def __call__(self, func_or_trainer):
        if self.func is None:
            self.func = func_or_trainer
            return self
        if self.should_run(func_or_trainer):
            self.func(func_or_trainer)

    def should_run(self, trainer):
        raise NotImplementedError()


class StepEvent(BaseEvent):

    def should_run(self, trainer):
        return True


class EvalStepEvent(BaseEvent):

    def should_run(self, trainer):
        return not trainer.state.is_training


class TrainStepEvent(BaseEvent):

    def should_run(self, trainer):
        return trainer.state.is_training


class EpochChangeEvent(BaseEvent):

    def __init__(self, call_on_first=True):
        BaseEvent.__init__(self)
        self.last_epoch = None
        self.call_on_first = call_on_first

    def should_run(self, trainer):
        current = trainer.state.epoch
        if self.last_epoch is None:
            self.last_epoch = current
            if self.call_on_first:
                return True
            else:
                return False
        if self.last_epoch != current:
            self.last_epoch = current
            return True
        return False


class EveryNthEvent(BaseEvent):

    def __init__(self, every_n, required_remainder=0):
        # required reminder=1 in order to trigger at the first call.
        BaseEvent.__init__(self)
        self.every_n = every_n
        self.required_remainder = required_remainder % every_n
        self.count = 0

    def should_run(self, trainer):
        self.count += 1
        return self.count % self.every_n == self.required_remainder


class TimeEvent(BaseEvent):

    def __init__(self, period, first_at=0):
        assert first_at <= period
        BaseEvent.__init__(self)
        self.period = period
        self.last = time.time() - (period - first_at)

    def should_run(self, trainer):
        t = time.time()
        if t >= self.last + self.period:
            self.last = t
            return True
        return False


if __name__ == '__main__':
    def update_fn(trainer, batch):
        trainer.state.add_scalar_data_point('loss', batch, smoothing=0.95)
        trainer.state.add_scalar_data_point('xx', batch, smoothing=0.95)
        time.sleep(0.1)
        return batch

    @EpochChangeEvent(5)
    def say_hello(trainer):
        print("hello new epoch!")

    st = STrainer(update_fn, events=[say_hello], tensorboard_log_dir='a')
    st.display_scalar_metric('xx')

    st.train(range(1000), steps=None)
    st.train(range(1000), steps=None)
    st.save('a')
    st.state = TrainerState()
    st.restore('a')
    st.train(range(1000), steps=None)
    import shutil
    shutil.rmtree('a')



