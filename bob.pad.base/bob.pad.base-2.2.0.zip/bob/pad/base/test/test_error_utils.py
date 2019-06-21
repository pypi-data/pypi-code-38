from bob.io.base.test_utils import datafile
from bob.io.base import HDF5File
from bob.pad.base.script.error_utils import (
    negatives_per_pai_and_positives,
    apcer_bpcer,
    calc_threshold,
)
import nose
import numpy as np

GENERATE_REFERENCES = False

scores_dev = datafile("per_pai_scores/scores-dev", module=__name__)
scores_dev_reference_mask = datafile(
    "per_pai_scores/scores-dev-{i}.hdf5", module=__name__
)


def _dump_dict(f, d, name):
    f[f"{name}_len"] = len(d)
    for i, (k, v) in enumerate(d.items()):
        f[f"{name}_key_{i}"] = k
        f[f"{name}_value_{i}"] = v


def _read_dict(f, name):
    ret = dict()
    for i in range(f[f"{name}_len"]):
        k = f[f"{name}_key_{i}"]
        v = f[f"{name}_value_{i}"]
        if isinstance(v, np.ndarray):
            v = v.tolist()
        ret[k] = v
    return ret


def test_per_pai_apcer():
    for i, regexps in enumerate((None, ["x[0-2]", "x[3-4]"], ["x[1-2]", "x[3-4]"])):
        try:
            pos, negs = negatives_per_pai_and_positives(scores_dev, regexps)
        except ValueError:
            if i == 2:
                continue
            raise
        all_negs = [s for scores in negs.values() for s in scores]

        thresholds = dict()
        for method in ("bpcer20", "far", "eer", "min-hter"):
            thresholds[method] = calc_threshold(
                method, pos, negs.values(), all_negs, far_value=0.1
            )

        metrics = dict()
        for method, threshold in thresholds.items():
            apcers, apcer, bpcer = apcer_bpcer(threshold, pos, *negs.values())
            metrics[method] = apcers + [apcer, bpcer]

        scores_dev_reference = scores_dev_reference_mask.format(i=i)
        if GENERATE_REFERENCES:
            with HDF5File(scores_dev_reference, "w") as f:
                f["pos"] = pos
                _dump_dict(f, negs, "negs")
                _dump_dict(f, thresholds, "thresholds")
                _dump_dict(f, metrics, "metrics")

        with HDF5File(scores_dev_reference, "r") as f:
            ref_pos = f["pos"].tolist()
            ref_negs = _read_dict(f, "negs")
            ref_thresholds = _read_dict(f, "thresholds")
            ref_metrics = _read_dict(f, "metrics")

        nose.tools.assert_list_equal(pos, ref_pos)
        nose.tools.assert_dict_equal(negs, ref_negs)
        nose.tools.assert_dict_equal(thresholds, ref_thresholds)
        nose.tools.assert_dict_equal(metrics, ref_metrics)
