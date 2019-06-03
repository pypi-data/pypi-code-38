""" module to plot choropleths """

from bokeh import plotting, models, io

import geoviz.preprocess as prc
from geoviz.params import DEFAULTFORMAT, PALETTES, HEIGHT_RATIO, get_palette_colors


def initialize_plot(formatting):
    """ Create Bokeh figure to which glyphs/elements can be added.

    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: Bokeh figure object """

    bkplot = plotting.figure(title=formatting['title'],
                             background_fill_color=formatting['background_color'],
                             plot_width=formatting['width'],
                             plot_height=int(formatting['width']*HEIGHT_RATIO),
                             tools=formatting['tools'])
    bkplot.title.text_font = formatting['font']
    bkplot.title.text_font_size = formatting['title_fontsize']
    bkplot.grid.grid_line_color = None
    bkplot.axis.visible = False
    bkplot.border_fill_color = None
    bkplot.outline_line_color = None
    return bkplot


def draw_main(bkplot, geo_df, y_var, y_type, geolabel, formatting):
    """ Adds choropleth based on specified y_var to an existing Bokeh plot.

    :param (Bokeh object) plot: pre-defined Bokeh figure
    :param (gpd.DataFrame) geo_df: merged geopandas DataFrame from merge_to_geodf()
    :param (str) y_var: column name of variable to plot
    :param (str) y_type: palette type: 'sequential', sequential_single', 'divergent', 'categorical'
    :param (str) geolabel: column name to use. default is county/state name from shapefile
    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: None (adds to Bokeh object) """

    geo_src = models.GeoJSONDataSource(geojson=geo_df.to_json())
    cmap = make_color_mapper(geo_df[y_var], y_type, formatting)

    shapes = bkplot.patches('xs', 'ys', fill_color={'field':y_var, 'transform': cmap},
                            fill_alpha=formatting['fill_alpha'],
                            line_color=formatting['line_color'],
                            line_width=formatting['line_width'], source=geo_src)
    if y_type != 'categorical':
        cbar = make_color_bar(cmap, formatting)
        bkplot.add_layout(cbar)

    hover = models.HoverTool(renderers=[shapes])
    hover_ylabel = y_var if formatting['hover_ylabel'] is None else formatting['hover_ylabel']
    hover.tooltips = [(formatting['hover_geolabel'], f'@{geolabel}'),
                      (hover_ylabel, f'@{y_var}{formatting["tooltip_text"]}')]
    bkplot.add_tools(hover)


def make_color_mapper(y_values, y_type, formatting):
    """ Generates color mapper which takes in values and outputs the color hexcode.

    :param (pd.Series) y_values: pandas Series to be plotted, for calculating min/max
    :param (str) y_type: 'sequential', 'divergent', or 'categorical' -- for palette
    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: Bokeh colormapper object """

    try:
        palette = PALETTES[y_type][formatting['palette']][formatting['ncolors']].copy()
    except KeyError: ## if palette is not in default list
        palette = get_palette_colors(formatting['palette'], formatting['ncolors']).copy()
    except TypeError: ## if formatting['palette'] is a list
        palette = formatting['palette'].copy()

    if formatting['reverse_palette']:
        palette.reverse()

    if y_type in ['sequential', 'divergent']:
        c_min = formatting['min'] if isinstance(formatting['min'], (int, float)) else min(y_values)
        c_max = formatting['max'] if isinstance(formatting['max'], (int, float)) else max(y_values)

        mapper_fx = {'lin':models.LinearColorMapper, 'log':models.LogColorMapper}
        mapper = mapper_fx[formatting['lin_or_log']](palette=palette, low=c_min, high=c_max)
    else:
        mapper = models.CategoricalColorMapper(factors=y_values.unique(), palette=palette)
    return mapper


def make_color_bar(cmap, formatting):
    """ Generates color bar from make_color_mapper()

    :param (Bokeh object) cmap: colormapper from make_color_mapper()
    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: None (adds to Bokeh object) """

    color_bar = models.ColorBar(color_mapper=cmap, label_standoff=10, location='bottom_right',
                                height=formatting['cbar_height'], background_fill_color=None,
                                major_label_text_font_size=formatting['cbar_fontsize'],
                                major_label_text_font=formatting['font'],
                                major_tick_line_color=formatting['cbar_tick_color'],
                                major_tick_line_alpha=formatting['cbar_tick_alpha'],
                                title=formatting['cbar_title'],
                                title_text_font_size=formatting['cbar_fontsize'],
                                title_text_font=formatting['font'],
                                title_text_align=formatting['cbar_title_align'],
                                title_text_font_style=formatting['cbar_style'],
                                title_standoff=int(formatting['width'] * \
                                                   formatting['cbar_title_standoff_ratio']))
    if formatting['cbar_textfmt']:
        color_bar.formatter = models.NumeralTickFormatter(format=formatting['cbar_textfmt'])
    return color_bar


def draw_state(bkplot, formatting):
    """ Adds a state choropleth (default is transparent fill) to an existing Bokeh plot.

    :param (Bokeh object) plot: pre-defined Bokeh figure
    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: None (adds to Bokeh object) """

    state_geojson = prc.shape_geojson('state', formatting['simplify']).to_json()
    state_source = models.GeoJSONDataSource(geojson=state_geojson)
    bkplot.patches('xs', 'ys', source=state_source,
                   fill_color=formatting['st_fill'], fill_alpha=formatting['st_alpha'],
                   line_color=formatting['st_line_color'], line_width=formatting['st_line_width'])


def draw_choropleth_layers(bkplot, geo_df, y_var, y_type, geolabel, formatting):
    """ Draws multi-layer choropleths (main + state outlines)

    :param (Bokeh object) plot: pre-defined Bokeh figure
    :param (gpd.DataFrame) geo_df: merged geopandas DataFrame from merge_to_geodf()
    :param (str) y_var: column name of variable to plot
    :param (str) y_type: 'sequential', 'divergent', or 'categorical' -- for palette
    :param (str) geolabel: column name to use. default is county/state name from shapefile
    :param (dict) formatting: see DEFAULTFORMAT from params.py
    :return: None (adds to Bokeh object) """

    if formatting['state_outline'] in ['before', 'both']:
        draw_state(bkplot, formatting)
    draw_main(bkplot, geo_df, y_var, y_type, geolabel, formatting)
    if formatting['state_outline'] == 'after':
        draw_state(bkplot, formatting)
    elif formatting['state_outline'] == 'both':
        temp_formatting = formatting.copy()
        temp_formatting['st_fill'] = None
        draw_state(bkplot, temp_formatting)


def save_plot(bkplot, output=False):
    """ Determines how choropleth plot is saved.

    :param (Bokeh object) plot: pre-defined Bokeh figure
    :param (str) output: filepath to save html file. if not specified, plots in notebook
    :return: None (adds to Bokeh object) """

    if output:
        io.output_file(output)
        io.save(bkplot, output)
    else:
        io.output_notebook(hide_banner=True)
        plotting.show(bkplot)


def plot(file_or_df, geoid_var, geoid_type, y_var, y_type, geolvl='county', geolabel='name',
         formatting=None, output=False, dropna=True):
    """Short summary.

    :param (str/pd.DataFrame) file_or_df: csv filepath or pandas/geopandas DataFrame with geoid_var
    :param (str) geoid_var: name of column containing the geo ID to match on
    :param (str) geoid_type: 'fips' (recommended), 'name', or 'abbrev' (state only)
    :param (str) y_var: column name of variable to plot
    :param (str) y_type: 'sequential', 'sequential_single' (hue), 'divergent', or 'categorical'
    :param (str) geolvl: 'county' or 'state'
    :param (str) geolabel: column name to use. default is county/state name from shapefile
    :param (dict) formatting: if custom dict is passed, update DEFAULTFORMAT with those key-values
    :param (str) output: if specified, filepath to save html file. see save_plot().
    :param (bool) dropna: default True, if false, keeps rows where y_var is nan.
    :return: if output is 'bokeh', returns Bokeh object; else None """

    ## get default plot formatting and update if necessary
    temp_format = DEFAULTFORMAT.copy()
    if formatting:
        temp_format.update(formatting)

    ## process data
    shape_df = prc.shape_geojson(geolvl, temp_format['simplify'])
    geo_df = prc.merge_to_geodf(shape_df, file_or_df, geoid_var, geoid_type, geolvl=geolvl)

    if dropna:
        geo_df = geo_df[geo_df[y_var].notnull()]

    ## plot and save choropleth
    bkplot = initialize_plot(temp_format)
    draw_choropleth_layers(bkplot, geo_df, y_var, y_type, geolabel, temp_format)

    if temp_format['svg']:
        bkplot.output_backend = 'svg'
    save_plot(bkplot, output)
    ## return to original state
    io.reset_output()

    return bkplot


def plot_empty(geo='state', formatting=None, output=False):
    """Generate map outline (no fill).

    :param (str) geo: 'state' or 'county'
    :param (dict) formatting: if custom dict is passed, update DEFAULTFORMAT with those key-values
    :param (str) output: if specified, filepath to save html file. see save_plot().
    :return: if output is 'bokeh', returns Bokeh object; else None """

    ## get default plot formatting and update if necessary
    temp_format = DEFAULTFORMAT.copy()
    if formatting:
        temp_format.update(formatting)

    ## process data
    shape_df = prc.shape_geojson(geo, temp_format['simplify'])
    geo_src = models.GeoJSONDataSource(geojson=shape_df.to_json())

    ## plot and save choropleth
    bkplot = initialize_plot(temp_format)
    bkplot.patches('xs', 'ys', fill_color=None, line_color=temp_format['line_color'],
                   line_width=temp_format['line_width'], source=geo_src)

    if temp_format['svg']:
        bkplot.output_backend = 'svg'
    save_plot(bkplot, output)
    ## return to original state
    io.reset_output()

    return bkplot
