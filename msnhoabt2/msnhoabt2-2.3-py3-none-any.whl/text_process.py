import re
import collections
import draw_helper as dr
import os
class Letter():
    def __init__(self,text,value):
        self.text=text;
        self.value=value;
    def __str__(self):
        return self.text+":"+str(self.value)

def words(text,regex):
    pattern = re.compile(regex)
    for match in pattern.finditer(text):
        yield match.group()

def phrases(words, xlen=2):
    phrase = []
    for word in words:
        phrase.append(word)
        if len(phrase) > xlen:
            phrase.remove(phrase[0])
        if len(phrase) == xlen:
            yield tuple(phrase)

def make_title(title,text,image_path,font_path, font_size, lang, tmp_path, logo_path, output):
    regex=r"[^\s]+"
    spacing=" "
    if(lang=='cn'):
        regex=r"[^\x00-\x7F]"
        spacing=""
    output, ext=os.path.splitext(output)
    output+=".jpg"
    counts = collections.defaultdict(int)
    list_title = list(phrases(words(title,regex)))
    list_content = list(phrases(words(text,regex)))
    list_total = list_title + list_content
    for phrase in list_total:
        counts[phrase] += 1
    list_words1 = {}
    list_words2 = {}
    list_words2[list_title[0][0]] = 1
    for phrase in list_title:
        list_words1[phrase[0]] = counts.get(phrase)
        list_words2[phrase[1]] = counts.get(phrase)
    list_words1[list_title[len(list_title) - 1][1]] = 1
    list_words_total = []
    #find top value
    arr_v = []
    for v in list_words1.values():
        if v not in arr_v:
            arr_v.append(v)
    arr_v.sort(reverse=True)
    for w in words(title,regex):
        list_words_total.append(Letter(w, max(list_words1.get(w), list_words2.get(w))))
    out_put_text=dr.write_text_on_logo(image_path, tmp_path,
                          list_words_total, arr_v,
                          font_path,None, font_size, spacing)
    dr.add_logo(out_put_text,logo_path,tmp_path,output)
    os.remove(out_put_text)
