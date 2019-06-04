"""
Single API approach for daytoday EDA charting requirements
Chart + Util = chartil

Invoking
| import KUtils.chartil as chartil

Entry api/function (Usage)
| chartilc.plot(dataframe, [list of column names])

Other available functions
| uni_category_barchart(df, column_name, limit_bars_count_to=10000, sort_by_value=False)
| uni_continuous_boxplot(df, column_name)
| uni_continuous_distplot(df, column_name)
| 
| bi_continuous_continuous_scatterplot(df, column_name1, column_name2, chart_type=None)
| bi_continuous_category_boxplot(df, continuous1, category2)
| bi_continuous_category_distplot(df, continuous1, category2)
| bi_category_category_crosstab_percentage(df, category_column1, category_column2)
| bi_category_category_stacked_barchart(df, category_column1, category_column2)
| bi_category_category_countplot(df, category_column1, category_column2)
| bi_continuous_category_violinplot(df, category1, continuous2)
| 
| multi_continuous_category_category_violinplot(df, continuous1, category_column2, category_column3)
| multi_continuous_continuous_category_scatterplot(df, column_name1, column_name2, column_name3)
| multi_continuous_category_category_boxplot(df, continuous1, category2, category3)
| multi_continuous_continuous_continuous_category_scatterplot(df, continuous1, continuous2, continuous3, category4)
| multi_continuous_continuous_continuous_scatterplot(df, continuous1, continuous2, continuous3, maintain_same_color_palette=False)


"""

# Import matplotlib & seaborn for charting/plotting
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import pandas as pd

# For 3D charts
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
from matplotlib.cm import cool

from KUtils.common import utils

base_color_list = ['green', 'red', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']


save_images = False
default_image_save_location = "d:\\temp\\plots"
default_dpi = 100
  
def plot(df, column_list, chart_type=None, optional_settings={}):    
    # Categorical column names
    categorical_columns = df[column_list].select_dtypes(include=['category', object]).columns.tolist()
    # Numerical/Continous column names 
    numerical_columns = [item for item in column_list if item not in categorical_columns]
    
    if chart_type=='heatmap':
        local_heatmap(df, numerical_columns, optional_settings)
    elif chart_type=='pairplot':
        multi_pairplot(df, column_list, optional_settings)
    else :  
        if len(column_list)==1: # Univariate
            if len(categorical_columns)>0 : 
                uni_category_barchart(df,column_list[0], optional_settings)
            else: # Dtype numeric or contnous variable
                if chart_type=='barchart': # Even though it is numerical you are forcing to use barchart using binning
                    no_of_bins = 10 
                    if optional_settings.get('no_of_bins')!=None:
                        no_of_bins = optional_settings.get('no_of_bins')
                        
                    start_idx = min(df[column_list[0]])
                    end_idx = max(df[column_list[0]])
                    step = (end_idx - start_idx)/no_of_bins
                    bin_labels = np.arange(start_idx, end_idx, step).tolist()
                    temp_column_name = 'tmp_'+column_list[0]
                    df[temp_column_name] = pd.cut(df[column_list[0]], no_of_bins, labels=bin_labels )
                    uni_category_barchart(df,temp_column_name, optional_settings)
                    del df[temp_column_name]
                elif chart_type=='distplot':
                    uni_continuous_distplot(df,column_list[0])
                else: # else boxplot
                    uni_continuous_boxplot(df,column_list[0]) # Default boxplot
        elif len(column_list)==2: # Bivariate or Segmented Univariate
            if len(categorical_columns)==2 : # Both are categorical
                if chart_type=='crosstab': # Percentage
                    bi_category_category_crosstab_percentage(df, categorical_columns[0], categorical_columns[1])
                elif chart_type=='stacked_barchart': # Stacked barchart
                    bi_category_category_stacked_barchart(df, categorical_columns[0], categorical_columns[1])
                else:
                    bi_category_category_countplot(df, categorical_columns[0], categorical_columns[1])
            elif len(numerical_columns)==2 : # Both are continous variable
                # Scatter plot
                bi_continuous_continuous_scatterplot(df,column_list[0], column_list[1], chart_type)
            else: # One is continous and other is categorical
                if chart_type=='distplot' :
                    bi_continuous_category_distplot(df, numerical_columns[0], categorical_columns[0])
                elif chart_type=='violinplot' :
                    bi_continuous_category_violinplot(df, numerical_columns[0], categorical_columns[0])
                else:
                    bi_continuous_category_boxplot(df, numerical_columns[0], categorical_columns[0])
                # Todo: What about other combination? category vs continuous
        elif len(column_list)==3: # Multi variate with three variables
            if len(numerical_columns)==3 : # All continous, plot 3D scatterplot
                multi_continuous_continuous_continuous_scatterplot(df, numerical_columns[0], numerical_columns[1], numerical_columns[2] )
            elif len(categorical_columns)==3: # All categorical
                multi_category_category_category_pairplot(df, categorical_columns[0], categorical_columns[1], categorical_columns[2] )                
            elif len(numerical_columns)==2:
                multi_continuous_continuous_category_scatterplot(df, numerical_columns[0], numerical_columns[1], categorical_columns[0], optional_settings)
            elif len(numerical_columns)==1:
                if chart_type=='violinplot': 
                    multi_continuous_category_category_violinplot(df, numerical_columns[0], categorical_columns[0], categorical_columns[1])
                else : 
                    multi_continuous_category_category_boxplot(df, numerical_columns[0], categorical_columns[0], categorical_columns[1])
                    # Todo: Any other combinations?
        elif len(column_list)==4:
            if len(numerical_columns)==3 :
                if chart_type=='bubbleplot':
                    multi_continuous_continuous_continuous_category_bubbleplot(df, numerical_columns[0], numerical_columns[1], numerical_columns[2], categorical_columns[0])
                else:
                    multi_continuous_continuous_continuous_category_scatterplot(df, numerical_columns[0], numerical_columns[1], numerical_columns[2], categorical_columns[0])
            else:
                 local_heatmap(df, numerical_columns, optional_settings)
        elif len(column_list)==5:
            if len(numerical_columns)==2 :
                multi_category_category_category_continuous_continuous_pairplot(df, categorical_columns[0], categorical_columns[1], categorical_columns[2],
                                                                                numerical_columns[0], numerical_columns[1])
            else :
                local_heatmap(df, numerical_columns, optional_settings)
        else :
            local_heatmap(df, numerical_columns, optional_settings)
            
def local_heatmap(df, column_list, optional_settings={}) :
    include_categorical = False
    if optional_settings.get('include_categorical')!=None:
        include_categorical = optional_settings.get('include_categorical')
    
    figuresize_width = (int)(0.80*len(column_list))
    figuresize_height = (int)(figuresize_width*.75)
        
    if include_categorical:
        df = utils.createDummies(df)
        column_list = df.columns.tolist() 
        figuresize_width = (int)(0.75*len(column_list))
        figuresize_height = (int)(figuresize_width*.66)
    
    plt.figure(figsize=(figuresize_width,figuresize_height))
    
    data_for_corelation = df[column_list].corr()
    
    if optional_settings.get('sort_by_column')!=None:
        sort_by_column = optional_settings.get('sort_by_column')
        #df_corr = heart_disease_df.corr()
        sort_a_column = data_for_corelation[sort_by_column].sort_values()
        data_for_corelation = data_for_corelation.reindex(sort_a_column.index)
        data_for_corelation = data_for_corelation[sort_a_column.index]
        
    sns.heatmap(data_for_corelation, annot=True) 

def multi_pairplot(df, column_list, optional_settings={}) :
    include_categorical = False
    if optional_settings.get('include_categorical')!=None:
        include_categorical = optional_settings.get('include_categorical')
    if include_categorical:
        df = utils.createDummies(df)
        column_list = df.columns.tolist() 
    group_by_last_column = False
    if optional_settings.get('group_by_last_column')!=None:
        group_by_last_column = optional_settings.get('group_by_last_column') 
    if group_by_last_column==True:
        sns.pairplot(df[column_list], hue=column_list[-1])
    else :
        sns.pairplot(df[column_list])
    
def add_value_labels(ax, spacing=5, include_percentage=True):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """
    total_count = 0
    if include_percentage:
        for rect in ax.patches:
            # Get X and Y placement of label from rect.
            total_count = total_count + rect.get_height()
          
    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with one decimal place
        label_value = "{:.0f}".format(y_value)
        if include_percentage:
            label_percent = "{:.2f}".format(y_value*100/total_count)
            label = label_value + ' (' + label_percent + '%)'
        else:
           label = label_value 
        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            ha='center',                # Horizontally center label
            va=va)                      # Vertically align label differently for
                                        # positive and negative values.
def core_barchart_from_series(aIndexSeries, optional_settings={}):
    data_for_chart = aIndexSeries
    
    exclude_zero_column = False
    if optional_settings.get('exclude_zero_column')!=None:
        exclude_zero_column = optional_settings.get('exclude_zero_column')
        
    if exclude_zero_column==True :
        data_for_chart = data_for_chart[data_for_chart!=0]
        
    sort_by_value=False
    sort_by_value=False
    if optional_settings.get('sort_by_value')!=None:
        sort_by_value = optional_settings.get('sort_by_value')
    
    if sort_by_value==False: # Use label as sorting
        data_for_chart = data_for_chart.sort_index()
    else:
        data_for_chart = data_for_chart.sort_values(ascending=False)
        
    limit_bars_count_to=10
    
    no_of_bars = len(data_for_chart)
    figuresize_width = 5+(int)(0.8*no_of_bars)
    figuresize_height = 3 + (int)(figuresize_width*.5)
    
    if sort_by_value==False: # Use label as sorting
        data_for_chart = data_for_chart.sort_index()
            
    ax = data_for_chart.plot(kind='bar',
                                    figsize=(figuresize_width,figuresize_height),
                                    title=optional_settings.get('chart_title'))
    ax.set_xlabel(optional_settings.get('x_label'))
    ax.set_ylabel(optional_settings.get('y_label'))
    add_value_labels(ax, include_percentage=False)
    
def uni_category_barchart(df, column_name, optional_settings={}): 
    # limit_bars_count_to=10000, sort_by_value=False):
    limit_bars_count_to = 1000
    if optional_settings.get('limit_bars_count_to')!=None:
        limit_bars_count_to = optional_settings.get('limit_bars_count_to')
        
    sort_by_value=False
    if optional_settings.get('sort_by_value')!=None:
        sort_by_value = optional_settings.get('sort_by_value')
        
    data_for_chart = df[column_name].value_counts(dropna=False)[:limit_bars_count_to]
    no_of_bars = len(data_for_chart)
    figuresize_width = 5+(int)(0.8*no_of_bars)
    figuresize_height = 2 + (int)(figuresize_width*.5)
    
    if sort_by_value==False: # Use label as sorting
        data_for_chart = data_for_chart.sort_index()
            
    ax = data_for_chart.plot(kind='bar',
                                    figsize=(figuresize_width,figuresize_height),
                                    title="Uni Categorical [" +column_name+"]")
    ax.set_xlabel("Categories in [" + column_name + "]")
    ax.set_ylabel("No. of Records or Rows per Category")
    add_value_labels(ax)
    if save_images:
        plt.savefig(default_image_save_location + "\\Uni_Barchart_" +column_name + ".png")
    
def uni_continuous_boxplot(df, column_name):
    sns.boxplot(y=df[column_name])    
    if save_images:
        plt.savefig(default_image_save_location + "\\Uni Continuous Boxplot-" +column_name+ ".png")
        
def uni_continuous_distplot(df, column_name):
    sns.distplot(df[column_name]) 
    if save_images:
        plt.savefig(default_image_save_location + "\\Uni Continuous Boxplot-" +column_name+ ".png")
        

def bi_continuous_continuous_scatterplot(df, column_name1, column_name2, chart_type=None):
    if chart_type=='regplot':
        sns.regplot(data=df, x=column_name1, y=column_name2)
    else:
        sns.scatterplot(data=df, x=column_name1, y=column_name2)
    if save_images:
        plt.savefig(default_image_save_location + "\\Bi Continuous Continuous Scatterplot-" +column_name1+" " + column_name2 + ".png")    

def bi_continuous_category_boxplot(df, continuous1, category2): 
    sns.boxplot(y=continuous1, x=category2, data=df)

def bi_continuous_category_distplot(df, continuous1, category2): 
    
    cat_unique_list = list(df[category2].unique())
    for col in cat_unique_list:
        subset = df[df[category2] == col]
        sns.distplot(subset[continuous1], hist = False, kde = True, kde_kws = {'shade': True, 'linewidth': 3}, label = col)
    
def multi_continuous_continuous_category_scatterplot(df, column_name1, column_name2, column_name3, optional_settings={}): 
    sns.scatterplot(data=df, x=column_name1, y=column_name2, hue=column_name3)
    
    show_label = False
    if optional_settings.get('show_label')!=None:
        show_label = optional_settings.get('show_label')
        
    if show_label==True:
        for i, txt in enumerate(df[column_name3]):
            plt.annotate(txt, (df[column_name1][i], df[column_name2][i]))
        
    if save_images:
        plt.savefig(default_image_save_location + "\\Multi Continuous Continuous Category Scatterplot-" +column_name1+" " + column_name2 + ".png", dpi = default_dpi)    

def multi_continuous_category_category_boxplot(df, continuous1, category2, category3): 
    sns.boxplot(y=continuous1, x=category2, hue=category3, data=df)


def bi_category_category_crosstab_percentage(df, category_column1, category_column2) :
    ct=pd.crosstab(df[category_column1], df[category_column2])
    ct.div(ct.sum(1).astype(float), axis=0).plot(kind="bar", stacked=True)
    
def bi_category_category_stacked_barchart(df, category_column1, category_column2) :   
    df.groupby([category_column1, category_column2]).size().unstack().plot.bar(stacked=True)
 
 
    
def bi_category_category_countplot(df, category_column1, category_column2) :
    sns.countplot(x=category_column1, hue=category_column2, data=df)

def bi_continuous_category_violinplot(df, category1, continuous2) :
    sns.violinplot(x=category1, y=continuous2, data=df, scale="count")

def multi_continuous_category_category_violinplot(df, continuous1, category_column2, category_column3):
    sns.violinplot(y=continuous1, x=category_column2, hue=category_column3, data=df, split=True, palette='muted')

def scaleTo01(x):
    return ((x-min(x))/(max(x)-min(x)))

def get_n_colors(n):
    return[ cool(float(i)/n) for i in range(n) ]
    
def multi_continuous_continuous_continuous_category_scatterplot(df, continuous1, continuous2, continuous3, category4):
    
    cat_unique_list = list(df[category4].unique())
    
    idx = [cat_unique_list.index(x) for x in cat_unique_list]
    colors = [base_color_list[i % len(base_color_list) ] for i in idx]
    color_dict = dict(zip(cat_unique_list, colors))

    fig = plt.figure(figsize=(8,8))
    # ax = Axes3D(fig)
    ax = plt.axes(projection='3d')
    
    ax.scatter(df[continuous1], df[continuous2], df[continuous3],  c=df[category4].map(color_dict))
    ax.set_xlabel(continuous1)
    ax.set_ylabel(continuous2)
    ax.set_zlabel(continuous3)
    ax.invert_yaxis()

    # Add legend with proxy artists
    column_pathces = [mpatches.Patch(color=colors[x], label=cat_unique_list[x]) for x in idx]
    plt.legend(handles=column_pathces, title=category4)
    

def multi_continuous_continuous_continuous_scatterplot(df, continuous1, continuous2, continuous3, maintain_same_color_palette=False):
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')
    #ax = Axes3D(fig)
    # ax = plt.axes(projection='3d')
    colors_df = df[[continuous1, continuous2, continuous3]]
    colors_df.columns = ['red', 'green', 'blue']
    if maintain_same_color_palette:
        if max(colors_df['red'])-min(colors_df['red']) > max(colors_df['green'])-min(colors_df['green']):
            colors_df = colors_df.rename(columns={'red': 'green', 'green': 'red'})    
            colors_df.head()
        if max(colors_df['red'])-min(colors_df['red']) > max(colors_df['blue'])-min(colors_df['blue']):
            colors_df = colors_df.rename(columns={'red': 'blue', 'blue': 'red'})    
            colors_df.head()
        if max(colors_df['green'])-min(colors_df['green']) > max(colors_df['blue'])-min(colors_df['blue']):
            colors_df = colors_df.rename(columns={'green': 'blue', 'blue': 'green'})    
            colors_df.head()
    colors_df = colors_df[['red','green','blue']].apply(scaleTo01)
    colors_array = colors_df.values    
    ax.scatter(df[continuous1], df[continuous2], df[continuous3],  facecolors=colors_array)
    ax.set_xlabel(continuous1)
    ax.set_ylabel(continuous2)
    ax.set_zlabel(continuous3)
    ax.invert_yaxis()    
    
def univariate_charts(data_frame):
    for column_name in data_frame.columns:        
        if pd.api.types.is_numeric_dtype(data_frame[column_name]):
            uni_continuous_boxplot(data_frame, column_name)
        elif pd.api.types.is_datetime64_dtype(data_frame[column_name]):
            print(column_name + ' Date')
        elif pd.api.types.is_categorical_dtype(data_frame[column_name]) or pd.api.types.is_object_dtype(data_frame[column_name]):
            uni_category_barchart(data_frame, column_name)
        else:
            print(column_name + 'Unknown')
            
            
def multi_category_category_category_pairplot(df, category1, category2, category3):
    grid = sns.FacetGrid(df, row=category1, col=category2, hue=category3, palette='seismic', size=4)
    grid.map(sns.countplot,  category3)
    grid.add_legend()
    
def multi_category_category_category_continuous_continuous_pairplot(df, 
            category1, category2, category3, continuous1, continuous2):    
    grid = sns.FacetGrid(df, row=category1, col=category2, hue=category3, palette='seismic', size=4)
    g = (grid.map(sns.scatterplot,  continuous1, continuous2, edgecolor="w").add_legend())
    
def multi_continuous_continuous_continuous_category_bubbleplot(df, continuous1, continuous2, continuous3, category1, maintain_same_color_palette=False):
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    #ax = Axes3D(fig)
    # ax = plt.axes(projection='3d')
    colors_df = df[[continuous1, continuous2, continuous3]]
    colors_df.columns = ['red', 'green', 'blue']
    if maintain_same_color_palette:
        if max(colors_df['red'])-min(colors_df['red']) > max(colors_df['green'])-min(colors_df['green']):
            colors_df = colors_df.rename(columns={'red': 'green', 'green': 'red'})    
            colors_df.head()
        if max(colors_df['red'])-min(colors_df['red']) > max(colors_df['blue'])-min(colors_df['blue']):
            colors_df = colors_df.rename(columns={'red': 'blue', 'blue': 'red'})    
            colors_df.head()
        if max(colors_df['green'])-min(colors_df['green']) > max(colors_df['blue'])-min(colors_df['blue']):
            colors_df = colors_df.rename(columns={'green': 'blue', 'blue': 'green'})    
            colors_df.head()
    colors_df = colors_df[['red','green','blue']].apply(scaleTo01)
    colors_array = colors_df.values
    
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    df['tmp_size'] = le.fit_transform(df[category1])*50 + 2
    ax.scatter(df[continuous1], df[continuous2], df[continuous3], s=df['tmp_size'], facecolors=colors_array)
    
        
    ax.set_xlabel(continuous1)
    ax.set_ylabel(continuous2)
    ax.set_zlabel(continuous3)
    ax.invert_yaxis() 
    
    