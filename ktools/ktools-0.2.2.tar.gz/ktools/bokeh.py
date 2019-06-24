import seaborn as sns
from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure, show


def scatter(x, y):
    source = ColumnDataSource(
        data=dict(
            x=x,
            y=y,
            desc=x.index,
        )
    )

    hover = HoverTool(
        tooltips=[
            ("(x,y)", "($x, $y)"),
            ("index", "@desc"),
        ]
    )

    p = figure(plot_width=1600, plot_height=700, tools=[hover, 'pan', 'box_zoom', 'reset'],
               title="Mouse over the dots")

    p.circle('x', 'y', size=5, source=source)
    show(p)


def multiple_scatter(x, multiple_y):
    hover = HoverTool(
        tooltips=[
            ("(x,y)", "(@x, @y)"),
            ("index", "@desc"),
        ]
    )

    p = figure(plot_width=1600, plot_height=1000, tools=[hover, 'wheel_zoom', 'pan', 'box_zoom', 'reset'],
               title="Mouse over the dots")

    colors = sns.color_palette("hls", len(multiple_y)).as_hex()
    for i, y in enumerate(multiple_y):
        p_x = x
        p_y = y
        source = ColumnDataSource(
            data=dict(
                x=p_x,
                y=p_y,
            )
        )
        p.circle('x', 'y', size=5, source=source, color=colors[i])
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    show(p)


def categorical_scatter(df, x_label, y_label, category_label, desc=None):
    hover = HoverTool(
        tooltips=[
            ("(x,y)", "(@x, @y)"),
            ("index", "@desc"),
        ]
    )
    if desc is None:
        desc = df[x_label].index

    p = figure(plot_width=1600, plot_height=1000, tools=[hover, 'wheel_zoom', 'pan', 'box_zoom', 'reset'],
               title="Mouse over the dots")

    categories = df[category_label]
    category_size = len(categories.unique())
    colors = sns.color_palette("hls", category_size).as_hex()
    name = df[category_label].name
    for i, category in enumerate(categories.unique()):
        p_x = df[df[name] == category][x_label]
        p_y = df[df[name] == category][y_label]
        p_desc = desc[df[name] == category]
        source = ColumnDataSource(
            data=dict(
                x=p_x,
                y=p_y,
                desc=p_desc,
            )
        )
        p.circle('x', 'y', size=5, source=source, color=colors[i], legend=str(category))
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    show(p)


def bar_plot(p_x):
    palette = sns.color_palette("hls", len(p_x)).as_hex()
    hover = HoverTool(
        tooltips=[
            ("(x,y)", "(@x, @y)"),
        ]
    )
    p = figure(x_range=p_x.index.astype(str).values, plot_width=800, plot_height=600, tools=[hover, 'wheel_zoom', 'pan', 'box_zoom', 'reset'])

    p_desc = p_x.index
    source = ColumnDataSource(
        data=dict(
            x=p_x.index.astype(str),
            y=p_x.values,
            color=palette
        ),
    )
    p.vbar('x', top='y', width=0.9, source=source, color='color')
    show(p)
