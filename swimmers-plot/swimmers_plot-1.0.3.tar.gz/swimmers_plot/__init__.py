"""Create a swimmer's plot of treatments for a cohort

To use:
cohort = swimmers_plot.Cohort()
cohort.load_samples('sample_inp.tsv')
cohort.load_treatments('treatment_inp.tsv')
cohort.make_swimmers_plot()
"""
import sys
if sys.version_info > (3,):
    from swimmers_plot.swimmers_plot import Cohort, Patient, Sample, Treatment
else:
    from swimmers_plot import Cohort, Patient, Sample, Treatment
