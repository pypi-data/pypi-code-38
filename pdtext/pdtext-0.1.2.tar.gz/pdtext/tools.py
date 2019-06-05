def clean_string(string):
    return string.strip('''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~''').lower()

def sentences(text):
    doc = nlp(text)
    sentences = []
    for s in doc.sents:
        sentences.append(s.text)
    df = pd.Series(sentences)
    return sentences

def tokens_to_rows(df_column):
    '''
    Takes an iterable column of a datframe and returns a dataframe
    where each item is now a row.
    '''

    df = pd.DataFrame(df_column.tolist()).stack()

    # clean up variable names
    df = df.reset_index()
    df.rename(index=str, columns={"level_0": "index",
                                  "level_1": "order",
                                  0 : 'token'}, inplace=True)
    df.sort_values(by=['index', 'order'], inplace = True)

    # set 'index ' column based on index of original df
    old_index = [df_column.index[i] for i in df['index'].values]
    df['index'] = old_index
    return df
