"""
This module provides a single string literal that is used to represent the
default tree pipeline configuration file. It also provides a function to write
this default configuration file to the disk.
"""

import os


tree_config_file = """\
[PipelineTask]
table={
  ".": ["RawCounts", {}],
  "raw": ["MakeRaw", {}],
  "removed": ["MakeRemoved", {}],
  "qnormed": ["MakeQnorm", {}],
  "cqn": ["MakeQnorm", {"condition_on": "% GC"}],
  "iced": ["MakeIced", {}],
  "kr": ["MakeKR", {}],
  "spline_both": ["MakeSpline", {}],
  "spline_gc": ["MakeSpline", {"bias_factors": ["% GC"], "knots": [0]}],
  "spline_length": ["MakeSpline", {"bias_factors": ["length"], "knots": [20]}],
  "express": ["MakeExpress", {}],
  "jointexpress": ["MakeJointExpress", {}],
  "bin_gmean_16_4": ["MakeBinned", {}],
  "bin_amean_20_8": ["MakeBinned", {"window_function": "amean",
                                    "bin_width": 8000,
                                    "window_width": 20000}],
  "bin_gmean_20_8": ["MakeBinned", {"bin_width": 8000,
                                    "window_width": 20000}],
  "expected_regional": ["MakeExpected", {"global_expected": false,
                                         "donut": false}],
  "expected_donut": ["MakeExpected", {}],
  "variance": ["MakeVariance", {}],
  "pvalues": ["MakePvalues", {}],
  "threshold": ["MakeThreshold", {}],
  "is": ["MakeInteractionScores", {}]
  }
tasks=[
  "./raw/qnormed/jointexpress/bin_gmean_16_4/expected_donut/variance/pvalues/threshold"
  ]

[RawCounts]
countsfiles={
  "rep1": "path/to/rep1.counts",
  "rep2": "path/to/rep2.counts"
  }

[PrimerFile]
primerfile=path/to/primerfile.bed

[MakeRaw]
outfile_pattern=%s_raw.counts
heatmap=True

[MakeRemoved]
outfile_pattern=%s_removed.counts
heatmap=True

[MakeQnorm]
outfile_pattern=%s_qnorm.counts
heatmap=True
regional=True
averaging=False

[MakeExpress]
outfile_pattern=%s_express.counts
heatmap=True

[MakeJointExpress]
outfile_pattern=%s_express.counts
heatmap=True

[MakeKR]
outfile_pattern=%s_kr.counts
imputation_size=0
heatmap=True

[MakeIced]
outfile_pattern=%s_iced.counts
imputation_size=0
heatmap=True

[MakeSpline]
outfile_pattern=%s_spline.counts
bias_factors=["% GC", "length"]
knots=[0, 20]
heatmap=True

[MakeSmoothed]
outfile_pattern=%s_smoothed.counts
heatmap=True
window_width=16000
window_function=gmean
threshold=0.0
wipe_unsmoothable_columns=False

[DetermineBins]
bin_width=4000

[MakeBinned]
outfile_pattern=%s_binned.counts
heatmap=True
bin_width=4000
window_width=16000
window_function=gmean
threshold=0.0
wipe_unsmoothable_columns=True

[MakeExpected]
outfile_pattern=%s_expected.counts
heatmap=True
monotonic=True
exclude_near_diagonal=True
powerlaw=False
regression=False
degree=1
lowess=False
lowess_frac=0.8
donut=True
p=5
w=15
donut_frac=0.2
min_exp=0.1
log_donut=True
max_with_lower_left=True
log_transform=auto
global_expected=False
plot_outfile=%d/expected-plots/%s_%r.png
plot_outfile_kde=False
plot_outfile_hexbin=True

[MakeObsMinusExp]
outfile_pattern=%s_obs_minus_exp.counts
heatmap=True

[MakeObsOverExp]
outfile_pattern=%s_obs_over_exp.counts
heatmap=True

[MakeVariance]
outfile_pattern=%s_variance.counts
model=lognorm
source=deviation
fitter=lowess
agg_fn=lowess
min_obs=2.0
min_disp=1e-8
min_dist=6
x_unit=dist
y_unit=disp
logx=False
logy=False
regional=False

[MakeCrossVariance]
outfile_pattern=%s_variance.counts
source=cross_rep
fitter=lowess
agg_fn=lowess
min_obs=2.0
min_disp=1e-8
min_dist=6
x_unit=dist
y_unit=disp
logx=False
logy=False
regional=False
conditions=ES,pNPC

[MakePvalues]
outfile_pattern=%s_pvalues.counts
heatmap=True
distribution=nbinom
log=False
vst=False

[MakeThreshold]
outfile_pattern=classifications.counts
heatmap=True
kappa_confusion_outfile=kappa_confusion.txt
dataset_outfile=dataset.tsv
significance_threshold=1e-15
bh_fdr=False
two_tail=False
concordant=False
distance_threshold=24000
size_threshold=3
background_threshold=0.6
conditions=ES,pNPC

[MakeQvalues]
outfile_pattern=%s_qvalues.counts
heatmap=True
method=fdr_bh

[MakeInteractionScores]
outfile_pattern=%s_IS.counts
heatmap=True

[MakeLogged]
outfile_pattern=%s_logged.counts

[core]
default-scheduler-host=yourscheduler.com
default-scheduler-port=80
default-scheduler-url=http://yourscheduler.com
rpc-connect-timeout=30

[worker]
count_uniques=True
keep_alive=True
retry_external_tasks=True
ping_interval=20
wait_interval=20

"""


def drop_config_file():
    """
    Drops the default config file in the current directory.
    """
    if os.path.exists('luigi.cfg'):
        raise IOError('luigi.cfg already exists here!')
    with open('luigi.cfg', 'w') as handle:
        handle.write(tree_config_file)
