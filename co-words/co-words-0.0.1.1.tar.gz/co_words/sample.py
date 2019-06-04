import pickle
from co_words.utilities import create_stop_words, clean_text, create_wc_dict
from co_words.wordcount import *

# ----- Load the data
with open('animal_farm/animal_farm_chapters.pickle', 'rb') as handle:
    wc_data = pickle.load(handle)
wc_data.head()

# ----- Clean the data
stop_words = create_stop_words()
wc_data['text_column'] = clean_text(wc_data['text_column'], stop_words=stop_words)
wc_data.head()


# ----------------------------------------------------------------------------------------------------------------------
# ----- Creating a Single Dictionary
wc_dict = create_wc_dict(wc_data, text_column='text_column', min_df=.0005)

wc = WordCount(wc_dict, stop_words)
print(wc.wc_data)

# ----------------------------------------------------------------------------------------------------------------------
# ----- Creating a WordCount object for each season in the documents
wc_objects = {}
for i in make_ordered_list(wc_dict['wc_data']['season']):
    print('Creating a WordCount object for: {}'.format(i))
    temp_info = filter_wc_dict(wc_dict, column='season', value=i)
    wc_objects[i] = WordCount(temp_info, stop_words)

print(wc_objects['Fall'].wc_data)


# ----------------------------------------------------------------------------------------------------------------------
# ----- Words Occurring With
# ----- Capabilities: Find words occurring with words from a list.
# --- Return unigrams or bigrams
# --- Return word counts, or document counts
# --- Return documents that do not contain the word_list
# ----------------------------------------------------------------------------------------------------------------------

ex1 = wc.words_occurring_with(['snowball', 'jones'],
                              when_multiple='OR', return_bigrams=True, doc_count=True, invert=False)
