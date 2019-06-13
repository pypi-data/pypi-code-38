from tests.extensions.common import *
from yo_extensions.misc import *
from yo_ml.metrics import roc_plot
import numpy as np
import unittest



class TestPlots(TestCase):
    def test_grpby_lines(self):
        df = Query.combinatorics.grid(a=[1,2,3],x=range(10)).select(lambda z: z.update(y=z.a*z.x)).to_dataframe()
        df.groupby('a').feed(plots.groupby.line('x','y').labels('groupby.line'))

    def test_grby_scatter(self):
        df = Query.combinatorics.grid(a=[1, 2, 3], x=range(10)).select(lambda z: z.update(y=z.a * z.x)).to_dataframe()
        df.groupby('a').feed(plots.groupby.scatter('x','y').labels('groupby.scatter'))

    def test_grby_bars(self):
        df = Query.combinatorics.grid(a=[1, 2, 3], x=range(10)).select(lambda z: z.update(y=z.a * z.x)).to_dataframe()
        df.groupby('a').feed(plots.groupby.bars('x','y').labels('groupby.bars'))

    def test_series_default(self):
        pd.Series([1,2,3]).feed(plots.series.default('bar'))

    def test_series_default_postproc(self):
        pd.Series(list(range(100))).feed(plots.series.default()
                                  .size(5,3)
                                  .labels('plotting with postprocessing','axis x','axis y')
                                  .with_legend()
                                  .tune(lambda ax: ax.set_xscale("log", nonposx='clip'))
                                  )

    def test_series_pie(self):
        pd.Series([1,2,3],name='pie').feed(plots.series.pie().labels('series.pie'))

    def test_series_pie_1(self):
        pd.Series([1, 2, 3], name='pie').feed(plots.series.pie(with_abs_values=True).labels('series.pie'))

    def test_series_funnel(self):
        pd.Series([1,2,3]).feed(plots.series.funnel().labels('series.funnel'))

    def test_series_hist(self):
        series = pd.Series(np.random.normal(size=1000))

        (Query
         .en([
            ('no_trimmer',alg.trimmer()),
            ('unite',alg.trimmer(unite_before=-1,unite_after=1)),
            ('unite_perc',alg.trimmer(unite_before_percentile=10,unite_after_percentile=90)),
            ('drop',alg.trimmer(drop_before=-1,drop_after=1)),
            ('drop_perc',alg.trimmer(drop_before_percentile=10,drop_after_percentile=90))
            ])
         .feed(fluq.with_plots(3, name_selector=lambda z: z[0]))
         .foreach(lambda z: series.feed(plots.series.hist(10,z.item[1]).on(z.ax)))
         )

    def test_df_heatmap(self):
        df = Query.combinatorics.grid(x=range(10),y=range(5)).select(lambda z: z.update(value=z.x-z.y)).to_dataframe()
        df.feed(plots.df.heatmap('x','y','value'))


    @unittest.skip
    def test_df_2d_hist(self):
        df = Query.en(zip(np.random.normal(size=1000),np.random.normal(size=1000))).select(lambda z: Obj(x=z[0],y=z[1])).to_dataframe()
        df = df.assign(x_cut = pd.cut(df.x,10), y_cut=pd.cut(df.y,10))
        df.groupby(['x_cut','y_cut']).size().to_frame('cnt').reset_index().feed(plots.df.heatmap('x_cut','y_cut','cnt'))

    def test_df_roc_curve(self):
        roc = pd.DataFrame(dict(
            true=[0, 0, 0, 0, 1, 1, 1],
            predicted=[0.1, 0.2, 0.3, 0.6, 0.5, 0.8, 0.9]
        ))
        roc.feed(roc_plot('true','predicted'))
