import bokeh.palettes
import holoviews as hv


def _no_xgrid_hook(plot, element):
    plot.handles['plot'].xgrid.grid_line_color = None

    
datashader_blues = bokeh.palettes.Blues9[:6][::-1]
datashader_greys = bokeh.palettes.Greys9[:6][::-1]
datashader_purples = bokeh.palettes.Purples9[:6][::-1]
datashader_reds = bokeh.palettes.Reds9[:6][::-1]

default_cmap = [
    "#4c78a8",
    "#f58518",
    "#e45756",
    "#72b7b2",
    "#54a24b",
    "#eeca3b",
    "#b279a2",
    "#ff9da6",
    "#9d755d",
    "#bab0ac",
]

def set_defaults():
    """
    Set convenient HoloViews defaults

    Called without arguments, sets default visual plotting options for
    HoloViews.
    """
    hv.opts.defaults(
        hv.opts.BoxWhisker(
            box_cmap=default_cmap,
            box_fill_alpha=0.75,
            box_line_color="black",
            box_width=0.4,
            cmap=default_cmap,
            height=350,
            hooks=[_no_xgrid_hook],
            legend_offset=(10, 100),
            legend_position="right",
            outlier_alpha=0.75,
            outlier_fill_color=None,
            outlier_fill_alpha=0,
            outlier_line_width=2,
            padding=0.05,
            show_grid=True,
            show_legend=False,
            show_title=True,
            toolbar="above",
            whisker_color="black",
            whisker_line_width=1,
            width=450,
        )
    )

    hv.opts.defaults(
        hv.opts.Curve(
            color=hv.Cycle(default_cmap),
            height=350,
            line_width=2,
            line_join="bevel",
            muted_line_alpha=0.1,
            padding=0.05,
            show_grid=True,
            toolbar="above",
            width=450,
        )
    )

    hv.opts.defaults(
        hv.opts.Histogram(
            fill_alpha=0.3,
            fill_color=hv.Cycle(default_cmap),
            height=450,
            line_alpha=1,
            line_width=2,
            padding=0.05,
            show_grid=True,
            show_legend=True,
            show_title=True,
            toolbar="above",
            width=500,
        )
    )

    hv.opts.defaults(
        hv.opts.NdOverlay(
            click_policy="hide",
            fontsize=dict(legend=8),
            height=350,
            legend_offset=(10, 100),
            legend_position="right",
            padding=0.05,
            show_grid=True,
            show_legend=True,
            show_title=True,
            toolbar="above",
            width=450,
        )
    )

    hv.opts.defaults(
        hv.opts.Overlay(
            click_policy="hide",
            fontsize=dict(legend=8),
            height=350,
            legend_offset=(10, 100),
            legend_position="right",
            padding=0.05,
            show_grid=True,
            show_legend=True,
            show_title=True,
            toolbar="above",
            width=450,
        )
    )


    hv.opts.defaults(
        hv.opts.Points(
            alpha=0.75,
            color=hv.Cycle(default_cmap),
            fill_alpha=0,
            fill_color=None,
            fontsize=dict(legend=8),
            height=350,
            legend_offset=(10, 100),
            legend_position="right",
            line_width=2,
            padding=0.05,
            show_grid=True,
            show_legend=True,
            show_title=True,
            size=5,
            toolbar="above",
            width=450,
        )
    )

    hv.opts.defaults(
        hv.opts.Scatter(
            alpha=0.75,
            cmap=bokeh.palettes.Viridis256,
            color=hv.Cycle(default_cmap),
            fill_alpha=0,
            fill_color=None,
            fontsize=dict(legend=8),
            height=350,
            legend_offset=(10, 100),
            legend_position="right",
            line_width=2,
            muted_line_alpha=0.1,
            padding=0.05,
            show_grid=True,
            size=5,
            toolbar="above",
            width=450,
        )
    )