import pandas as pd
import numpy as np
import os.path as op
from copy import deepcopy
import fitz
import random


def str2color(label):
    """Generates a color randomly from a string
    :param label: a string
    :return:a triplet representing a color
    """
    if label :
        color_str = str(label).split("-/-")[0]
        color = (0.3 + 0.5 * random.Random(color_str + 'a').random(),
                 0.3 + 0.5 * random.Random(color_str + 'c').random(),
                 0.3 + 0.5 * random.Random(color_str + 'b').random())

    else :
        color = (1,0,0)

    return color


def _add_square_from_coordinates(x, y, w, h, label, page):
    """

    :param x: coordinate x of the rectangle
    :param y: coordinate y
    :param w: width of the rectangle
    :param h: height of the rectangle
    :param label: label labelling the annotation
    :param page: Fitz page where to make the square
    :return: None, but the page has been annotated according to the arguments
    """
    rectangle = fitz.Rect(x, y, x + w, y + h)

    annot = page.addRectAnnot(rectangle)
    annot.setInfo({'content': f'{label}', 'name': '', 'title': '', 'creationDate': '', 'modDate': '', 'subject': ''})
    annot.setColors({"stroke": str2color(
        label)})  # annot.setColors({"stroke":(0, 0, 1), "fill":(0.75, 0.8, 0.95)}) (Red, Yellow, Blue)
    annot.setBorder({'width': 1.5})
    annot.update(fill_color=None)


def _add_annotation_from_text(text, label, page, type, debug=False):
    """Adds an annotation to a Pymupdf (fitz) pdf page
    :param annot_text: a string to look for in the pdf
    :param label: the label to give to this text
    :param page: the page number where the text can be found
    :param annot_type: 'Highlight' or 'Square' : the type of the annotations to make
    :return: None, but the page has been annotated according to the arguments
    """
    text.strip()
    rl = page.searchFor(text, hit_max=200)
    print(len(rl), rl) if debug else 0

    if rl:  #  If there's a match
        if type == 'Square':
            rectangle_encompass = fitz.Rect(min(w[0] for w in rl), min(w[1] for w in rl),
                                            max(w[2] for w in rl), max(w[3] for w in rl))

            annot = page.addRectAnnot(rectangle_encompass)
            annot.setInfo({'content': f'{label}', 'name': '', 'title': '', 'creationDate': '', 'modDate': '',
                           'subject': ''})
            annot.setColors({"stroke": str2color(
                label)})  # annot.setColors({"stroke":(0, 0, 1), "fill":(0.75, 0.8, 0.95)}) (Red, Yellow, Blue)
            annot.setBorder({'width': 1.5})
            annot.update(fill_color=None)  # donc on peut faire des polyline_highlights avec fill_color = False ?

            print('Func(add_annotation) -- added Square') if debug else 0

        elif type == 'Highlight':
            print('Highlight') if debug else 0
            if len(rl) == 1:
                annot = page.addHighlightAnnot(rl[0])
                annot.setInfo({'content': f'{label}', 'name': '', 'title': '', 'creationDate': '', 'modDate': '',
                               'subject': ''})
                annot.setColors({"stroke": str2color(label)})
                annot.update(fill_color=None)
                #  Add color annotation

            elif len(rl) > 1:
                for ix, k in enumerate(rl):
                    annot = page.addHighlightAnnot(k)
                    annot.setInfo({'content': f'{label}-/-{ix + 1}', 'name': '', 'title': '', 'creationDate': '',
                                   'modDate': '', 'subject': ''})
                    annot.setColors({"stroke": str2color(label)})
                    annot.update(fill_color=None)

            print("Func(add_annotation) -- added 'HighLight'") if debug else 0

        else:
            print('WARNING: IncorrectSetting: incorrect annotation type detected')

    elif text == '':
        print("nothing to be found ") if debug == True else 0

    else:
        print(f'WARNING: NotFound: text to annotate is not found in page {page}') if debug == True else 0


def annotate_pdf(adf, pdf_path, dest_pdf_path, debug=False):
    """Takes a dataframe of annotations (adf) with minimal set of columns and
    :param adf: the adf containing info on what to annot on the pdf : must either have column 'text' or column 'x','y','w' and 'h'.
    :param pdf_path:the directory of the pdf you want to annot following the adf "instructions"
    :param dest_pdf_path: the path where to store the new pdf
    :return: None, but the pdf has been annotated accordingly and copied at the same directory with the name 'pdf_name' + '-marked.pdf'.
    """

    if not isinstance(adf, pd.DataFrame):
        raise Exception(f'TypeError : expected pd.Dataframe for adf, yet received object of type : {type(adf)}')

    if not op.exists(pdf_path):
        raise Exception(f'FileNotFound: pdf_path not exists at {pdf_path}')

    if not op.exists(op.dirname(dest_pdf_path)):
        raise Exception(f'DirNotFound: the directory of dest_pdf_path not exists at {op.dirname(dest_pdf_path)}')

    pdf = fitz.open(pdf_path)

    if not ('label' in adf.columns):
        adf['label'] = ''

    adf['label'].replace('', np.NaN).fillna('', inplace=True)

    if not ('type' in adf.columns):
        adf['type'] = 'Square'

    adf['type'].replace('', np.NaN).fillna('Square', inplace=True)

    for ix, row in adf.iterrows():
        if 'page' in row and row['page'] and row['page'] == row['page']:
            if all(c in row for c in 'xywh') and all(row[c] for c in 'xywh') and all(row[c] == row[c] for c in 'xywh'):
                print("Square : ", row['x'], row['y'], row['w'], row['h'], row['label'], pdf[int(row['page'] - 1)]) if debug else 0
                _add_square_from_coordinates(row['x'], row['y'], row['w'], row['h'], row['label'], pdf[int(row['page'] - 1)])

            elif 'text' in row and row['text'] and row['text'] == row['text']:
                print('HERE', row['text'], row['type']) if debug else 0
                _add_annotation_from_text(row['text'], row['label'], pdf[row['page'] - 1], row['type'])

            else:
                print('WARNING no annot_text column nor coordinates provided')

        else:

            if len(pdf) == 1:
                if all(c in row for c in 'xywh') and all(row[c] for c in 'xywh') and all(row[c] == row[c] for c in 'xywh'):
                    print("Square : ", row['x'], row['y'], row['w'], row['h'], row['label'], pdf[0]) if debug else 0
                    _add_square_from_coordinates(row['x'], row['y'], row['w'], row['h'], row['label'], pdf[0])

                elif 'text' in adf.columns:
                    print("Highlighting : ", row['text'], row['label'], pdf[0], row['type']) if debug else 0
                    _add_annotation_from_text(row['text'], row['label'], pdf[0], row['type'])

                else:
                    print('WARNING no annot_text column nor coordinates provided')

            elif 'text' in adf.columns:
                print("Highlighting : ", row['text'], row['label'], row['type']) if debug else 0
                for page in pdf:
                    print("Highlighting : ", row['text'], row['label'], page, row['type'])  if debug else 0
                    _add_annotation_from_text(row['text'], row['label'], page, row['type'])

            else:
                print('WARNING no annot_text column nor page column in adf')

    pdf.save(dest_pdf_path)
    print(f'PDF saved at : {dest_pdf_path}') if debug else 0
    return dest_pdf_path



if __name__ == '__main__':
    # from scuts import visuallize_df
    # from shared import RESSOURCES_DIR
    #
    # pdf_path = op.join(RESSOURCES_DIR, 'pdf_test_annot_3.pdf')
    # adf = pd.DataFrame({'annot_text': ['by air or by water;',
    #                                    'the word mark ‘FEELING’, filed on 5 J vehicles ;; trees and transmissions for land vehicles;'],
    #                     'annot_type': ['Highlight', 'Square'],
    #                     'label': ['highlight', 'square'],
    #                     'page' : [1, 1]})
    # annotate_pdf(adf, pdf_path, '/home/antoine/PycharmProjects/pdfannot/ressources/pdf_test_annot_3.pdf-marked')
    #
    # # Test dlf2adf
    # df = pd.read_excel(RESSOURCES_DIR + '/seraphin/20020207_R1035_2000-2_FR.xlsx')
    # pdf_path = RESSOURCES_DIR + '/seraphin/20020207_R1035_2000-2_FR.pdf'
    # dest_pdf_path = RESSOURCES_DIR + '/seraphin/20020207_R1035_2000-2_FR_annotated.pdf'
    # adf = dlf2adf(df)
    # annotate_pdf(adf, pdf_path, dest_pdf_path)

    # test square_from_coordinate

    pdf_path = '/home/antoine/Desktop/ACHORD -Kbis-01-08-2018.pdf'
    dest_pdf_path = '/home/antoine/Desktop/ACHORD -Kbis-01-08-2018_annotated.pdf'
    adf = pd.read_excel('/home/antoine/Desktop/ACHORD -Kbis-01-08-2018 - annot.xlsx')
    annotate_pdf(adf, pdf_path, dest_pdf_path)
