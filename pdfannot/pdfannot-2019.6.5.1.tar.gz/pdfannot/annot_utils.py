import pandas as pd


def dlf2adf(dlf):
    """Transforms a Dataframe so that it matches genannot requirements
    :param dlf: a data frame with one column per label of annotation. WARNING : each of them must be name annot_{label_name}
    :return: a data frame with the three columns required by annotate_pdlf
    """

    frames = []
    for c in dlf.columns:
        if 'annot_' not in c:
            continue

        adf1 = dlf[dlf[c].notnull()]
        adf1 = adf1[['page', c]]
        adf1.rename(columns={c: 'text'}, inplace=True)
        adf1['label'] = c[6:]

        frames.append(adf1)

    adf = pd.concat(frames)
    adf['text'] = adf['text'].astype(str)

    for index, row in adf.iterrows():
        if ' ;; ' in row['text']:
            l = row['text'].split(' ;; ')
            for annot in l:
                new_row = row
                new_row['text'] = annot
                adf = adf.append(new_row)

    adf.drop_duplicates(inplace=True, subset=['text', 'page'])

    return adf

