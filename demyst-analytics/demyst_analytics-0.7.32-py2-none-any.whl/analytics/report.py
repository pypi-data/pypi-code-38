import pandas as pd
import numpy as np
import re

from IPython.display import display, Markdown, HTML

def attribute_construct(in_data, out_data):
    df = pd.DataFrame({
        'column': np.setdiff1d(out_data.columns.values, in_data.columns.values)
    })

    # split connector and attribute
    re_connector = [re.search('^([^\\.]*)\\.(.*)$', a) for a in df.column]
    df['connector'] = [r.group(1) for r in re_connector]
    df['attribute'] = [r.group(2) for r in re_connector]

    # Find how nested the attribute is
    re_nested = [re.findall('\\[(\d*)\\]', a) for a in df.attribute]
    df['nested_level'] = [(np.array(r).astype(int)+1).prod() for r in re_nested]

    # Strip out the nesting from the attribute
    df['attribute'] = [re.sub('\\[\d*\\]', '[*]', a) for a in df.attribute]

    return df

def attribute_collapse(attributes):
    max_nested = (
        attributes.groupby(['connector', 'attribute'])[['nested_level']].max().
        reset_index().rename(columns={'nested_level':'max_nested'})
    )
    level_1 = attributes.query('nested_level == 1').drop(columns='nested_level').rename(columns={'column': 'column_0'})
    df_collapsed = pd.merge(max_nested, level_1, how='left', on=['connector', 'attribute'])
    return df_collapsed

def connector_cost(attributes, analytics):
    c = attributes[['connector']].drop_duplicates()
    c['cost'] = [analytics.C.provider_cost(c) if c!="inputs" else 0 for c in c.connector]
    return pd.merge(attributes, c, how='left', on='connector')

def connector_matched(attributes, data):
    stacked = (
        data.notna()[attributes.column_0].stack().reset_index().
        rename(columns={'level_0': 'row', 'level_1': 'column_0', 0: 'not_na'})
    )
    stacked = pd.merge(stacked, attributes[['connector', 'column_0']], how='left', on='column_0')

    stacked = stacked.groupby(['connector', 'row'])['not_na'].any().reset_index()

    any_match = stacked.groupby('connector')['not_na'].sum().astype(int).reset_index().rename(columns={'not_na': 'connector_match'})
    return pd.merge(attributes, any_match, how='left', on='connector')

def attribute_types(attributes, data) :
    types = (
        data[attributes['column_0']].dtypes.reset_index().
        rename(columns={'index': 'column_0', 0:'type'})
    )
    return pd.merge(attributes, types, how='left', on='column_0')

def attribute_fill(attributes, data) :
    fill = (
        data[attributes['column_0']].replace(r'^\s*$', np.nan, regex=True).count().reset_index().
        rename(columns={'index': 'column_0', 0:'attribute_fill'})
    )
    return pd.merge(attributes, fill, how='left', on='column_0')

def attribute_nunique(attributes, data) :
    unique = (
        data[attributes['column_0']].nunique().reset_index().
        rename(columns={'index': 'column_0', 0:'attribute_nunique'})
    )
    return pd.merge(attributes, unique, how='left', on='column_0')

def attribute_cleanup(attributes, data):
    clean = (
        attributes.assign(
            match_rate=attributes.connector_match.astype(float) / len(data),
            fill_rate=attributes.attribute_fill.astype(float) / attributes.connector_match,
            nunique=attributes.attribute_nunique
        )[['connector', 'attribute', 'type', 'max_nested', 'match_rate', 'fill_rate', 'nunique', 'column_0']]
    )
    # Assume objects are strings
    return clean

def attribute_display(attributes):
    kept_connectors = attributes.connector.drop_duplicates().values

    for c in kept_connectors:
        sub = attributes[attributes.connector == c].copy().reset_index()
        display(Markdown("### %s" % sub.connector[0]))
        display(Markdown("*%0.0f%% match rate  --  %d attributes*" % (
                    sub.match_rate[0]*100, len(sub))))
        sub = sub.drop(columns=['index', 'connector', 'match_rate', 'column_0'])
        sub = sub.sort_values(['fill_rate', 'attribute'], ascending=False)
        display(sub)

def report(inputs, enriched):
    attributes = attribute_construct(inputs, enriched)
    attributes = attribute_collapse(attributes)
    attributes = connector_matched(attributes, enriched)
    attributes = attribute_types(attributes, enriched)
    attributes = attribute_fill(attributes, enriched)
    attributes = attribute_nunique(attributes, enriched)
    attributes = attribute_cleanup(attributes, enriched)

    return attributes
