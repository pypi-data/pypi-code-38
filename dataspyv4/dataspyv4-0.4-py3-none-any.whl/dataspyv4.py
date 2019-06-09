from . import utils
from . import centraltendency as ct
from . import categoryfucntion as cf
from . import charts


pct=10
maxcat=20

def setPercentage(x):
    global pct
    pct = x

def setMaxCatg(x):
    global maxcat
    maxcat=x

def analyse(dataFrame,col,extra=False,chart=False,findanomalies=False):
    x=dataFrame[col]
    utils.setIndex(col)
    df=utils.concat(ct.mean(x),ct.median(x),ct.mode(x))
    df=utils.concat(df,ct.rng(x))
    df = utils.concat(df, ct.unique(x))
    df = utils.concat(df, ct.missing(x))
    df.columns = [ 'Mean', 'Median', 'Mode', 'Range', '%Unique', '%Missing']
    before = utils.getColumns(df)
    if extra == True:
        if utils.isCategory(x, pct, maxcat) == False:
            df = utils.concat(df, ct.skew(x))
            df = utils.concat(df, ct.var(x))
            df = utils.concat(df, ct.std(x))
            df = utils.concat(df, ct.min(x))
            df = utils.concat(df, ct.max(x))
            df = utils.concat(df, ct.iqr(x))
            df = utils.concat(df, utils.isCategory(x,pct,maxcat))
            cols = ['Skewness', 'Variance', 'SD', 'Min', 'Max', 'InterQuartileRng', 'IsCategorical']
            df.columns = utils.extend(before, cols)
        else:
            df = utils.concat(df, cf.top_catg(dataFrame,col))
            df = utils.concat(df, cf.top_value(dataFrame,col))
            df = utils.concat(df, utils.isCategory(x, pct, maxcat))
            cols = ['Top Category', 'Top Fequency', 'IsCategorical']
            df.columns = utils.extend(before, cols)
    if chart == True:
        if (utils.isContinous(x, pct, maxcat)):
            charts.continous_graph(dataFrame, col,pct,maxcat)
        else:
            charts.catg_graph(dataFrame, col)

    return df

