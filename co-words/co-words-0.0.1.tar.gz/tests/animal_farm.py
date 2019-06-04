"""
Animal Farm book was obtained from: http://gutenberg.net.au/ebooks01/0100011h.html
"""

import pandas as pd
import pickle

text = []
for i in range(1, 11):
    with open("animal_farm/chapter_" + str(i), 'r') as myfile:
        t = myfile.read().replace('\n', '')
    text.append(t)

wc_data = pd.DataFrame()
wc_data['chapter'] = ["Chapter " + str(i) for i in range(1, 11)]
wc_data['id'] = [i for i in range(1, 11)]
wc_data['season'] = ['Spring', 'Summer', 'Fall', 'Winter',
                     'Spring', 'Summer', 'Fall', 'Winter', 'Spring', 'Summer']
wc_data['text_column'] = text

with open('animal_farm/animal_farm_chapters.pickle', 'wb') as handle:
    pickle.dump(wc_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
