# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

from .config import get_config
from .connection import get_backend_session


class Predictor(object):
    """
    Please email lcp-beta@comet.ml for comments or questions.
    """

    def __init__(
        self, experiment, loss_name="loss", patience=10, best_callback=None, **defaults
    ):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.config = get_config()
        self.experiment = experiment
        self.loss_name = loss_name
        self.patience = patience
        self.best_callback = best_callback
        self.step = None
        self.done = None
        self.wait = 0
        self.best = None
        self.loss = []
        self.defaults = {
            "experiment_key": self.experiment.id,
            "api_key": self.experiment.api_key,
            "threshold": 0.1,
            "TS": self.loss,  # Reference!
            "HP_samples": float("nan"),
            "AP_no_parameters": float("nan"),
            "HP_epochs": float("nan"),
            "HP_learning_rate": float("nan"),
            "HP_batch_size": float("nan"),
        }
        self.set_defaults(**defaults)
        self.base_url = self.config["comet.predictor_url"]
        self.status_url = "{}lc_predictor/status/".format(self.base_url)
        self.predict_url = "{}lc_predictor/predict/".format(self.base_url)
        self._session = get_backend_session()
        status = self.status()
        self.experiment.log_other("predictor_loss_name", self.loss_name)
        self.experiment.log_other("predictor_id", status["model_id"])

    def reset(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.step = None
        self.wait = 0
        self.best = None
        self.loss[:] = []  # Reference!

    def set_defaults(self, **defaults):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.defaults.update(defaults)

    def status(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            response = self._session.get(self.status_url)
        except Exception:
            pass
        else:
            if response.status_code == 200:
                response_data = response.json()
                return response_data
        return None

    def report_loss(self, loss, step=None):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.step = step
        self.loss.append(loss)
        self.experiment.log_metric("predictor_tracked_loss", loss, step=self.step)

    def stop_early(self, patience=None, **data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        patience = patience if patience is not None else self.patience
        defaults = self.defaults.copy()
        defaults.update(data)
        if len(self.loss) < 1:
            return False
        if self.done is not None:
            (lower, mean, upper) = self.done
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_upper": upper,
                    "predictor_lower": lower,
                    "predictor_threshold": defaults["threshold"],
                    "predictor_patience": patience,
                    "predictor_wait": self.wait,
                },
                step=self.step,
            )
            return True
        lmu = self.get_prediction(**data)
        if lmu is None:
            return False
        (lower, mean, upper) = lmu
        current_loss = self.loss[-1]
        lowest_min = min(self.loss[:-1])
        self.experiment.log_metrics(
            {
                "predictor_mean": mean,
                "predictor_upper": upper,
                "predictor_lower": lower,
                "predictor_threshold": defaults["threshold"],
                "predictor_patience": patience,
                "predictor_wait": self.wait,
            },
            step=self.step,
        )
        epoch = self.step if self.step is not None else self.experiment.curr_step
        if lowest_min < upper:
            if lowest_min <= mean:
                self.experiment.log_other("predictor_stop_step", epoch)
                self.experiment.log_other("predictor_stop_reason", "threshold crossed")
                self.done = (lower, mean, upper)
                return True
            elif current_loss < lowest_min:
                self.wait = 0
                self.best = (current_loss, self.experiment.curr_step)
                if callable(self.best_callback):
                    self.best_callback(self, current_loss)
            else:
                self.wait += 1
        else:
            self.wait += 1
        if self.wait >= patience:
            self.experiment.log_other("predictor_stop_step", epoch)
            self.experiment.log_other("predictor_stop_reason", "patience exceeded")
            self.done = (lower, mean, upper)
            return True
        return False

    def get_prediction(self, **data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        request_data = self.defaults.copy()
        # Update from one-time overrides:
        request_data.update(data)
        response = self._session.post(self.predict_url, json={"data": request_data})
        if response.status_code == 200:
            data = response.json().get("response")
            return (data["min"], data["mean"], data["max"])
        elif response.status_code == 201:
            return None
        else:
            raise Exception(
                "Invalid Predictor request for %s: %s" % (request_data, response)
            )
