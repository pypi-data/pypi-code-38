#!/usr/bin/env python


import mpu.io
import yaml
import pandas as pd


def get_language_data():
    url = ("http://www.iana.org/assignments/"
           "language-subtag-registry/language-subtag-registry")
    data = mpu.io.urlread(url)
    data = data.split('%%')
    languages = []
    last_key = None
    for el in data:
        language = {}
        for line in el.split('\n'):
            if len(line) == 0:
                continue
            if line.startswith('  '):
                language[last_key] += ' ' + line.strip()
                continue
            key, value = line.strip().split(': ')
            last_key = key
            language[key] = value
        languages.append(language)
    return languages


def filter_languages(data):
    print(data[0])
    data = data[1:]

    df = pd.DataFrame(data)
    df = df.drop(columns=['Tag', 'Prefix'])
    print('Found {} languages.'.format(len(data)))

    mask = df['Deprecated'].isna()
    nb_deprecated = sum(~mask)
    df = df[mask]
    print('Remove deprecated: {} ({} remaining)'
          .format(nb_deprecated, len(df)))
    df = df.drop(columns=['Deprecated'])

    mask = df['Type'] == 'language'
    nb_non_language = sum(~mask)
    df = df[mask]
    print('Remove non-language: {} ({} remaining)'
          .format(nb_non_language, len(df)))
    df = df.drop(columns=['Type'])

    mask = df['Scope'].isna()
    nb_non_language = sum(~mask)
    df = df[mask]
    print('Remove non-language: {} ({} remaining)'
          .format(nb_non_language, len(df)))
    df = df.drop(columns=['Scope', 'Comments', 'Added', 'Preferred-Value'])


if __name__ == '__main__':
    languages = get_language_data()

    with open('languages.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(languages,
                  outfile,
                  default_flow_style=False,
                  allow_unicode=True)
