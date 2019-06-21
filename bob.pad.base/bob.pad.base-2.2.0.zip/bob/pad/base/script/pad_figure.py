"""Runs error analysis on score sets, outputs metrics and plots"""

import bob.measure.script.figure as measure_figure
from bob.measure.utils import get_fta_list
from bob.measure import farfrr, precision_recall, f_score
import bob.bio.base.script.figure as bio_figure
from .error_utils import calc_threshold, apcer_bpcer
import click
from tabulate import tabulate
import numpy as np


def _normalize_input_scores(input_score, input_name):
    pos, negs = input_score
    # convert scores to sorted numpy arrays and keep a copy of all negatives
    pos = np.ascontiguousarray(pos)
    pos.sort()
    all_negs = np.ascontiguousarray([s for neg in negs.values() for s in neg])
    all_negs.sort()
    # FTA is calculated on pos and all_negs so we remove nans from negs
    for k, v in negs.items():
        v = np.ascontiguousarray(v)
        v.sort()
        negs[k] = v[~np.isnan(v)]
    neg_list, pos_list, fta_list = get_fta_list([(all_negs, pos)])
    all_negs, pos, fta = neg_list[0], pos_list[0], fta_list[0]
    return input_name, pos, negs, all_negs, fta


class Metrics(bio_figure.Metrics):
    """Compute metrics from score files"""

    def __init__(self, ctx, scores, evaluation, func_load, names):
        if isinstance(names, str):
            names = names.split(",")
        super(Metrics, self).__init__(ctx, scores, evaluation, func_load, names)

    def get_thres(self, criterion, pos, negs, all_negs, far_value):
        return calc_threshold(
            criterion,
            pos=pos,
            negs=negs.values(),
            all_negs=all_negs,
            far_value=far_value,
            is_sorted=True,
        )

    def _numbers(self, threshold, pos, negs, all_negs, fta):
        pais = list(negs.keys())
        apcer_pais, apcer, bpcer = apcer_bpcer(threshold, pos, *[negs[k] for k in pais])
        apcer_pais = {k: apcer_pais[i] for i, k in enumerate(pais)}
        acer = (apcer + bpcer) / 2.0
        fpr, fnr = farfrr(all_negs, pos, threshold)
        hter = (fpr + fnr) / 2.0
        far = fpr * (1 - fta)
        frr = fta + fnr * (1 - fta)

        nn = all_negs.shape[0]  # number of attack
        fp = int(round(fpr * nn))  # number of false positives
        np = pos.shape[0]  # number of bonafide
        fn = int(round(fnr * np))  # number of false negatives

        # precision and recall
        precision, recall = precision_recall(all_negs, pos, threshold)

        # f_score
        f1_score = f_score(all_negs, pos, threshold, 1)
        metrics = dict(
            apcer_pais=apcer_pais,
            apcer=apcer,
            bpcer=bpcer,
            acer=acer,
            fta=fta,
            fpr=fpr,
            fnr=fnr,
            hter=hter,
            far=far,
            frr=frr,
            fp=fp,
            nn=nn,
            fn=fn,
            np=np,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
        )
        return metrics

    def _strings(self, metrics):
        n_dec = ".%df" % self._decimal
        for k, v in metrics.items():
            if k in ("precision", "recall", "f1_score"):
                metrics[k] = "%s" % format(v, n_dec)
            elif k in ("np", "nn", "fp", "fn"):
                continue
            elif k in ("fpr", "fnr"):
                if "fp" in metrics:
                    metrics[k] = "%s%% (%d/%d)" % (
                        format(100 * v, n_dec),
                        metrics["fp" if k == "fpr" else "fn"],
                        metrics["np" if k == "fpr" else "nn"],
                    )
                else:
                    metrics[k] = "%s%%" % format(100 * v, n_dec)
            elif k == "apcer_pais":
                metrics[k] = {
                    k1: "%s%%" % format(100 * v1, n_dec) for k1, v1 in v.items()
                }
            else:
                metrics[k] = "%s%%" % format(100 * v, n_dec)

        return metrics

    def _get_all_metrics(self, idx, input_scores, input_names):
        """ Compute all metrics for dev and eval scores"""
        for i, (score, name) in enumerate(zip(input_scores, input_names)):
            input_scores[i] = _normalize_input_scores(score, name)

        dev_file, dev_pos, dev_negs, dev_all_negs, dev_fta = input_scores[0]
        if self._eval:
            eval_file, eval_pos, eval_negs, eval_all_negs, eval_fta = input_scores[1]

        threshold = (
            self.get_thres(self._criterion, dev_pos, dev_negs, dev_all_negs, self._far)
            if self._thres is None
            else self._thres[idx]
        )

        title = self._legends[idx] if self._legends is not None else None
        if self._thres is None:
            far_str = ""
            if self._criterion == "far" and self._far is not None:
                far_str = str(self._far)
            click.echo(
                "[Min. criterion: %s %s] Threshold on Development set `%s`: %e"
                % (self._criterion.upper(), far_str, title or dev_file, threshold),
                file=self.log_file,
            )
        else:
            click.echo(
                "[Min. criterion: user provided] Threshold on "
                "Development set `%s`: %e" % (dev_file or title, threshold),
                file=self.log_file,
            )

        res = []
        res.append(
            self._strings(
                self._numbers(threshold, dev_pos, dev_negs, dev_all_negs, dev_fta)
            )
        )

        if self._eval:
            # computes statistics for the eval set based on the threshold a priori
            res.append(
                self._strings(
                    self._numbers(
                        threshold, eval_pos, eval_negs, eval_all_negs, eval_fta
                    )
                )
            )
        else:
            res.append(None)

        return res

    def compute(self, idx, input_scores, input_names):
        """ Compute metrics for the given criteria"""
        title = self._legends[idx] if self._legends is not None else None
        all_metrics = self._get_all_metrics(idx, input_scores, input_names)
        headers = [" " or title, "Development"]
        if self._eval:
            headers.append("Evaluation")
        rows = []

        for name in self.names:
            if name == "apcer_pais":
                for k, v in all_metrics[0][name].items():
                    print_name = f"APCER ({k})"
                    rows += [[print_name, v]]
                    if self._eval:
                        rows[-1].append(all_metrics[1][name][k])
                continue
            print_name = name.upper()
            rows += [[print_name, all_metrics[0][name]]]
            if self._eval:
                rows[-1].append(all_metrics[1][name])

        click.echo(tabulate(rows, headers, self._tablefmt), file=self.log_file)


class MultiMetrics(Metrics):
    """Compute metrics from score files"""

    def __init__(self, ctx, scores, evaluation, func_load, names):
        super(MultiMetrics, self).__init__(
            ctx, scores, evaluation, func_load, names=names
        )
        self.rows = []
        self.headers = None
        self.pais = None

    def _compute_headers(self, pais):
        names = list(self.names)
        if "apcer_pais" in names:
            idx = names.index("apcer_pais")
            names = (
                [n.upper() for n in names[:idx]]
                + self.pais
                + [n.upper() for n in names[idx + 1 :]]
            )
        self.headers = ["Methods"] + names
        if self._eval and "hter" in self.names:
            self.headers.insert(1, "HTER (dev)")

    def _strings(self, metrics):
        formatted_metrics = dict()
        for name in self.names:
            if name == "apcer_pais":
                for pai in self.pais:
                    mean = metrics[pai].mean()
                    std = metrics[pai].std()
                    mean = super()._strings({pai: mean})[pai]
                    std = super()._strings({pai: std})[pai]
                    formatted_metrics[pai] = f"{mean} ({std})"
            else:
                mean = metrics[name].mean()
                std = metrics[name].std()
                mean = super()._strings({name: mean})[name]
                std = super()._strings({name: std})[name]
                formatted_metrics[name] = f"{mean} ({std})"

        return formatted_metrics

    def _structured_array(self, metrics):
        names = list(metrics[0].keys())
        if "apcer_pais" in names:
            idx = names.index("apcer_pais")
            pais = list(f"APCER ({pai})" for pai in metrics[0]["apcer_pais"].keys())
            names = names[:idx] + pais + names[idx + 1 :]
            self.pais = self.pais or pais
        formats = [float] * len(names)
        dtype = dict(names=names, formats=formats)
        array = []
        for each in metrics:
            array.append([])
            for k, v in each.items():
                if k == "apcer_pais":
                    array[-1].extend(list(v.values()))
                else:
                    array[-1].append(v)
        array = [tuple(a) for a in array]
        return np.array(array, dtype=dtype)

    def compute(self, idx, input_scores, input_names):
        """Computes the average of metrics over several protocols."""
        for i, (score, name) in enumerate(zip(input_scores, input_names)):
            input_scores[i] = _normalize_input_scores(score, name)

        step = 2 if self._eval else 1
        self._dev_metrics = []
        self._thresholds = []
        for scores in input_scores[::step]:
            name, pos, negs, all_negs, fta = scores
            threshold = (
                self.get_thres(self._criterion, pos, negs, all_negs, self._far)
                if self._thres is None
                else self._thres[idx]
            )
            self._thresholds.append(threshold)
            self._dev_metrics.append(self._numbers(threshold, pos, negs, all_negs, fta))
        self._dev_metrics = self._structured_array(self._dev_metrics)

        if self._eval:
            self._eval_metrics = []
            for i, scores in enumerate(input_scores[1::step]):
                name, pos, negs, all_negs, fta = scores
                threshold = self._thresholds[i]
                self._eval_metrics.append(
                    self._numbers(threshold, pos, negs, all_negs, fta)
                )
            self._eval_metrics = self._structured_array(self._eval_metrics)

        title = self._legends[idx] if self._legends is not None else name

        dev_metrics = self._strings(self._dev_metrics)

        if self._eval and "hter" in dev_metrics:
            self.rows.append([title, dev_metrics["hter"]])
        elif not self._eval:
            row = [title]
            for name in self.names:
                if name == "apcer_pais":
                    for pai in self.pais:
                        row += [dev_metrics[pai]]
                else:
                    row += [dev_metrics[name]]
            self.rows.append(row)
        else:
            self.rows.append([title])

        if self._eval:
            eval_metrics = self._strings(self._eval_metrics)
            row = []
            for name in self.names:
                if name == "apcer_pais":
                    for pai in self.pais:
                        row += [eval_metrics[pai]]
                else:
                    row += [eval_metrics[name]]

            self.rows[-1].extend(row)

        # compute header based on found PAI names
        if self.headers is None:
            self._compute_headers(self.pais)

    def end_process(self):
        click.echo(
            tabulate(self.rows, self.headers, self._tablefmt), file=self.log_file
        )
        super(MultiMetrics, self).end_process()


class Roc(bio_figure.Roc):
    """ROC for PAD"""

    def __init__(self, ctx, scores, evaluation, func_load):
        super(Roc, self).__init__(ctx, scores, evaluation, func_load)
        self._x_label = ctx.meta.get("x_label") or "APCER"
        default_y_label = "1-BPCER" if self._semilogx else "BPCER"
        self._y_label = ctx.meta.get("y_label") or default_y_label


class Det(bio_figure.Det):
    def __init__(self, ctx, scores, evaluation, func_load):
        super(Det, self).__init__(ctx, scores, evaluation, func_load)
        self._x_label = ctx.meta.get("x_label") or "APCER (%)"
        self._y_label = ctx.meta.get("y_label") or "BPCER (%)"


class Hist(measure_figure.Hist):
    """ Histograms for PAD """

    def _setup_hist(self, neg, pos):
        self._title_base = "PAD"
        self._density_hist(pos[0], n=0, label="Bona-fide", color="C1")
        self._density_hist(
            neg[0],
            n=1,
            label="Presentation attack",
            alpha=0.4,
            color="C7",
            hatch="\\\\",
        )
