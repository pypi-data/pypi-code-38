import altair as alt
from IPython.display import display


def altair_init():
    alt.renderers.enable('notebook')
    alt.data_transformers.enable('default', max_rows=None)
    alt.themes.enable('opaque')  # for dark background color
    #alt.data_transformers.enable('json')


def altair_plot_bar_with_date_tab(df, x, y, dt, freq="year", agg_method="sum", w=1000, h=400, count_as_bar_width=True):
    """
    x,y の bar plot を dtのタブで選択 (shiftで複数選択可能)

    count_as_bar_width: Trueなら要素数をバーの太さに反映する

    dt: shiftを押しながらだと、複数選択可能

    agg_method: "sum","mean","median","count","min","max", ...
        https://vega.github.io/vega-lite/docs/aggregate.html#ops

    freq: 
    "year", "yearquarter", "yearquartermonth", "yearmonth", "yearmonthdate", "yearmonthdatehours", "yearmonthdatehoursminutes"
    "quarter", "quartermonth"
    "month", "monthdate"
    "date" (Day of month, i.e., 1 - 31)
    "day" (Day of week, i.e., Monday - Friday)
    "hours", "hoursminutes", "hoursminutesseconds"
    "minutes", "minutesseconds"
    "seconds", "secondsmilliseconds"
    "milliseconds"
    https://vega.github.io/vega-lite/docs/timeunit.html

    example
    altair_plot_bar_with_date_tab(df, x="業種", y="profit", dt="決算発表日")
    altair_plot_bar_with_date_tab(df, x="業種", y="profit", dt="決算発表日", w=1000, h=400,)
    altair_plot_bar_with_date_tab(df, x="業種", y="profit", dt="決算発表日", freq="month",)
    altair_plot_bar_with_date_tab(df, x="業種", y="profit", dt="決算発表日", freq="yearmonth", h=1000)


    """

    selection_year = alt.selection_multi(encodings=['y'], empty="all")  # fields には :N :Q などの型を入れたらダメ
    clr_year = alt.condition(selection_year, alt.ColorValue("#77c"), alt.ColorValue("#eee"))

    bar_width = alt.Size("count()", scale=alt.Scale(range=(5, 25)),) if count_as_bar_width else alt.Size()

    y = "{}({}):Q".format(agg_method, y)
    tab = "{}({})".format(freq, dt)

    base = alt.Chart(data=df)

    legend_year = base.mark_circle(size=300).encode(
        alt.Y(tab),
        color=clr_year,
        tooltip=[tab],
    ).add_selection(
        selection_year,
    ).properties(
        height=h,
        width=50,
    )

    chart = base.mark_bar().encode(
        x=x,
        y=alt.Y(y,),
        #color=alt.Color(x, legend=None),
        color=x,
        size=bar_width,
        tooltip=[x, y, alt.Tooltip("count()", aggregate="count", title="count")],
    ).transform_filter(
        selection_year,
    ).properties(
        width=w,
        height=h,
    )

    display(legend_year | chart)
    return
