"""
This module provides a single string literal that is used to represent the
default pipeline configuration file. It also provides a function to write this
default configuration file to the disk.
"""

import os


config_file = """\
[PipelineTask]
step_order=["MakeExpress", "MakeBinned", "MakeExpected", "MakeLegacyPvaluesOne"]
initial_level=fragment

[RawCounts]
countsfiles={"rep1": "path/to/rep1.counts", "rep2": "path/to/rep2.counts"}

[PrimerFile]
primerfile=path/to/primerfile.bed

[MakeRemoved]
outfile_pattern=removed/%s_removed.counts
heatmap=True

[QnormInnerTask]
outfile_pattern=qnorm/%s_qnorm.counts
heatmap=True
regional=False
averaging=False

[MakeExpress]
outfile_pattern=express/%s_express.counts
heatmap=True

[JointExpressInnerTask]
outfile_pattern=express/%s_express.counts
heatmap=True

[MakeKR]
outfile_pattern=kr/%s_kr.counts
imputation_size=0
heatmap=True

[MakeIced]
outfile_pattern=iced/%s_iced.counts
imputation_size=0
heatmap=True

[MakeSpline]
outfile_pattern=spline/%s_spline.counts
bias_factors=["% GC", "length"]
knots=[10, 20]
heatmap=True

[DetermineBins]
bin_width=4000

[MakeBinned]
outfile_pattern=binned/%s_binned.counts
heatmap=True
window_width=20000
window_function=gmean
threshold=0.0
wipe_unsmoothable_columns=True

[MakeExpected]
outfile_pattern=expected/%s_expected.counts
heatmap=True
monotonic=False
regression=True
degree=1
lowess=False
lowess_frac=0.5
donut=False
p=5
w=15
donut_frac=0.2
log_donut=False
max_with_lower_left=False
log_transform=auto
global_expected=False
plot_outfile=expected-plots/%s_%r.png
plot_outfile_kde=False
plot_outfile_hexbin=True

[MakeLegacyPvaluesOne]
outfile_pattern=pvalues/%s_pvalues.counts
heatmap=True
mode=obs_over_exp
dist=norm
log=True

[MakeVariancePlots]
mode=obs_over_exp
dist=norm
log=True

[MakeSelectedFits]
mode=obs_over_exp
dist=norm
log=True

[MakeShiftedFits]
dist=norm
log=True

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
        handle.write(config_file)
