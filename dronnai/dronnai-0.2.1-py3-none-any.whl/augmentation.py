import os
import pandas as pd
from google.cloud import translate
from tqdm import tqdm


class GoogleTranslationClient:
    def __init__(self, cred_path=None):
        import os
        if cred_path is not None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path

        from google.cloud import translate
        self.client = translate.Client()

    def get_all_langs(self):
        return [lang['language'] for lang in self.client.get_languages()]

    def translate(self, texts, source_lang, target_lang):
        return [text['translatedText'] for text in \
                self.client.translate(texts, source_language=source_lang,
                                             target_language=target_lang)]

def augment_data(client, inputs, labels, langs='all', source_lang='pl', drop_duplicates=True):
    from tqdm import tqdm
    import pandas as pd
    
    source_texts = inputs
    
    if langs == 'all':
        langs = client.get_all_langs()
        
    aug_texts = []
    langs_column = [source_lang]*len(source_texts)
    n_langs = 1
    for lang in tqdm(langs):
        try:
            translated_texts = client.translate(source_texts, source_lang=source_lang, target_lang=lang)
            aug_texts += client.translate(translated_texts, source_lang=lang, target_lang=source_lang)
            langs_column += [lang]*len(translated_texts)
            n_langs += 1
        except:
            print(f'Language {lang} cannot be used.')
        
    aug_df = pd.DataFrame({'input': source_texts + aug_texts, 'label': labels*n_langs, 'lang': langs_column})
    
    if drop_duplicates:
        aug_df.drop_duplicates(subset='input', inplace=True)
        
    return aug_df.input.tolist(), aug_df.label.tolist(), aug_df.lang.tolist()