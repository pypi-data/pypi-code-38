#!/usr/bin/env python

import argparse
import warnings
import sys
import imp

import lib5c
from lib5c.tools.hic_extract import add_hic_extract_tool
from lib5c.tools.trim import add_trim_tool
from lib5c.tools.outliers import add_outliers_tool
from lib5c.tools.remove import add_remove_tool
from lib5c.tools.qnorm import add_qnorm_tool
from lib5c.tools.express import add_express_tool
from lib5c.tools.kr import add_kr_tool
from lib5c.tools.spline import add_spline_tool
from lib5c.tools.determine_bins import add_determine_bins_tool
from lib5c.tools.bin import add_bin_tool
from lib5c.tools.smooth import add_smooth_tool
from lib5c.tools.expected import add_expected_tool
from lib5c.tools.variance import add_variance_tool
from lib5c.tools.pvalues import add_pvalues_tool
from lib5c.tools.threshold import add_threshold_tool
from lib5c.tools.pvalue_histogram import add_pvalue_histogram_tool
from lib5c.tools.heatmap import add_heatmap_tool
from lib5c.tools.distribution import add_distribution_tool
from lib5c.tools.dd_curve import add_dd_curve_tool
from lib5c.tools.visualize_fits import add_visualize_fits_tool
from lib5c.tools.visualize_variance import add_visualize_variance_tool
from lib5c.tools.correlation import add_correlation_tool
from lib5c.tools.pca import add_pca_tool
from lib5c.tools.boxplot import add_boxplot_tool
from lib5c.tools.bias_heatmap import add_bias_heatmap_tool
from lib5c.tools.visualize_splines import add_visualize_splines_tool
from lib5c.tools.subtract import add_subtract_tool
from lib5c.tools.divide import add_divide_tool
from lib5c.tools.log import add_log_tool
from lib5c.tools.qvalues import add_qvalues_tool
from lib5c.tools.interaction_score import add_interaction_score_tool
from lib5c.tools.colorscale import add_colorscale_tool
from lib5c.tools.pipeline import add_pipeline_tool
from lib5c.tools.iced import add_iced_tool
from lib5c.tools.enrichment import add_enrichment_tool
from lib5c.tools.convergency import add_convergency_tool

try:
    imp.find_module('luigi')
    luigi_avail = True
except ImportError:
    luigi_avail = False

try:
    imp.find_module('iced')
    iced_avail = True
except ImportError:
    iced_avail = False


class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        return ''

    def format_help(self):
        help = super(CustomHelpFormatter, self).format_help()
        return '\n'.join(filter(
            lambda x: not (x.startswith('positional') or x.startswith('  {')),
            help.split('\n')
        ))


def lib5c_toolbox(argv=sys.argv[1:]):
    warnings.simplefilter('ignore')
    root_parser = argparse.ArgumentParser(prog='lib5c',
                                          formatter_class=CustomHelpFormatter)
    root_parser.add_argument(
        '-v', '--version',
        action='version',
        version='lib5c version %s' % lib5c.__version__)

    subparsers = root_parser.add_subparsers(help='sub-commands', prog='lib5c')
    if luigi_avail:
        add_pipeline_tool(subparsers)
    add_hic_extract_tool(subparsers)
    add_trim_tool(subparsers)
    add_outliers_tool(subparsers)
    add_remove_tool(subparsers)
    add_qnorm_tool(subparsers)
    add_express_tool(subparsers)
    add_kr_tool(subparsers)
    add_spline_tool(subparsers)

    if iced_avail:
        add_iced_tool(subparsers)

    add_determine_bins_tool(subparsers)
    add_bin_tool(subparsers)
    add_smooth_tool(subparsers)
    add_expected_tool(subparsers)
    add_variance_tool(subparsers)
    add_pvalues_tool(subparsers)
    add_threshold_tool(subparsers)
    add_qvalues_tool(subparsers)
    add_interaction_score_tool(subparsers)
    add_subtract_tool(subparsers)
    add_divide_tool(subparsers)
    add_log_tool(subparsers)
    add_colorscale_tool(subparsers)

    plot_parser = subparsers.add_parser('plot', help='plot things',
                                        formatter_class=CustomHelpFormatter)
    plot_subparsers = plot_parser.add_subparsers(help='sub-commands')
    add_pvalue_histogram_tool(plot_subparsers)
    add_heatmap_tool(plot_subparsers)
    add_distribution_tool(plot_subparsers)
    add_dd_curve_tool(plot_subparsers)
    add_visualize_fits_tool(plot_subparsers)
    add_visualize_variance_tool(plot_subparsers)
    add_correlation_tool(plot_subparsers)
    add_pca_tool(plot_subparsers)
    add_boxplot_tool(plot_subparsers)
    add_bias_heatmap_tool(plot_subparsers)
    add_visualize_splines_tool(plot_subparsers)
    add_enrichment_tool(plot_subparsers)
    add_convergency_tool(plot_subparsers)

    args = root_parser.parse_args(argv)
    args.func(root_parser, args)


if __name__ == '__main__':
    lib5c_toolbox()
