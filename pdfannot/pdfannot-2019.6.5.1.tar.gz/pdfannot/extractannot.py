import pandas as pd
import numpy as np
import os.path as op
from copy import deepcopy
import fitz
from operator import itemgetter
from itertools import groupby


def _extract_word_from_highlight(annot, words, debug=False):
    """Extracts words behind a hightlight
    :param annot: a highlight annotation to extract words from. Warning : if it is followed by others
    highlight annotations which labels are named specifically ('same_label'+ -/- 'next_integer'),
     their words will be extracted too.
     :param words: the words of the page containing the annot.
     :param debug: debug param
    :return: the list of words extracted and the annotation which may have changed.
    """

    mywords = []

    #  If the hightlight spans on multiple text boxes (possibly multiple lines
    if len(annot.vertices) > 4:

        for k in range(len(annot.vertices) // 4):
            rectangle = fitz.Rect(annot.vertices[k * 4][0], annot.vertices[k * 4][1],
                                  annot.vertices[k * 4 + 3][0], annot.vertices[k * 4 + 3][1])

            for w in words:
                r = deepcopy(rectangle)
                area_intersect = r.intersect(fitz.Rect(w[:4])).getRectArea()
                area_word = fitz.Rect(w[:4]).getRectArea()

                if area_intersect / area_word > 0.6:
                    mywords.append(w)

    else:
        mywords += [w for w in words if
                    annot.rect.intersect(fitz.Rect(w[:4])).getRectArea() / fitz.Rect(w[:4]).getRectArea() > 0.6]

        if annot.next and annot.next.info['content']:
            label_next = annot.next.info['content']
            print(annot.next.info) if debug else 0

            while annot.next and annot.next.info['content'] and label_next[(len(label_next) - 4):(len(label_next) - 1)] == '-/-' and int(label_next[len(label_next) - 1]) > 1:
                annot = annot.next
                mywords += [w for w in words if
                            annot.rect.intersect(fitz.Rect(w[:4])).getRectArea() / fitz.Rect(w[:4]).getRectArea() > 0.6]
                if annot.next and annot.next.info['content']:
                    label_next = annot.next.info['content']

    return mywords, annot


def pdfannot2df(input_pdf, debug=False):
    """Takes an annotated pdf as an input and transforms it into a dlf
    :param input_pdf: path to the pdf.
    :return:the adf corresponding to the pdf's annotations
    """

    pdf = fitz.open(input_pdf)
    l, order = [], 0
    for ixpage, page in enumerate(pdf):
        tmp = {'page': ixpage + 1, 'pdf_path': input_pdf, 'page_width': page.rect[2], 'page_height': page.rect[3]}
        words = page.getTextWords()
        annot = page.firstAnnot
        print('annot : ', annot) if debug else 0
        print('page : ', ixpage) if debug else 0
        while annot:
            print('type annot : ', annot.type[1]) if debug else 0
            mywords = []

            if annot.type[1] == 'Highlight':
                mywords, annot = _extract_word_from_highlight(annot, words)

            elif annot.type[1] == 'Square':
                mywords = [w for w in words if
                           annot.rect.intersect(fitz.Rect(w[:4])).getRectArea() / fitz.Rect(w[:4]).getRectArea() > 0.6]

            else:
                print('encountered an annotation different from "Square" and "Highlights".') if debug else 0

            # This word sorting is actually useless as it is worse than the one fitz does by default.
            # mywords.sort(key=itemgetter(3, 0))  # sort by y1, x0 of the word rect
            # group = groupby(mywords, key=itemgetter(3))
            annot_text = " ".join(w[4] for w in mywords)
            print(mywords) if debug else 0

            order += 1
            print('order : ', order) if debug else 0
            tmp.update({'x': int(annot.rect[0]), 'y': int(annot.rect[1]),
                        # Those might be wrong for multi line highlights as the rect only
                        # correspond to the one of the last line
                        'w': int(annot.rect[2] - annot.rect[0]), 'h': int(annot.rect[3] - annot.rect[1]),
                        'type': annot.type[1], 'label': annot.info['content'], 'order': order,
                        'text': annot_text})
            print(tmp) if debug else 0
            l.append(deepcopy(tmp))

            annot = annot.next

    adf = pd.DataFrame(l)
    print('adf : ', adf) if debug else 0

    if adf.empty :
        print(f'WARNING : the document {input_pdf} does not contain any annotations, the returned dataframe is empty.')

    elif adf[adf['type'].isnull()].shape[0]:
        raise Exception(f'Missing {adf[adf["type"].isnull()].shape[0]} type annotation(s) in {input_pdf}')

    else :
        final_columns = ['order', 'page', 'x', 'y', 'w', 'h', 'type', 'label', 'page_height', 'page_width',
                     'pdf_path', 'text']
        adf = adf[final_columns]

    return adf


if __name__ == '__main__':
    from scuts import visuallize_df
    from shared import RESSOURCES_DIR

    input_pdf = RESSOURCES_DIR + '/facture_for_testing_word_order.pdf'
    df = pdfannot2df(input_pdf)
