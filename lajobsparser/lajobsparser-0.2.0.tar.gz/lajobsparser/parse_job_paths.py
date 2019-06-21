import pathlib
import logging

from typing import List

from collections import namedtuple

import pandas as pd

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from pdfminer.pdfpage import PDFPage

from pdfminer.layout import LAParams

from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTCurve
from pdfminer.layout import LTFigure
from pdfminer.layout import LTLine


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
# log_name = '.'.join(pathlib.Path(__file__).parts[-2:])
log = logging.getLogger(__name__)


def is_in_box(box_in, box_out):
    if all([
            box_out.bbox[0] <= box_in.bbox[0],
            box_out.bbox[2] >= box_in.bbox[2],
            box_out.bbox[1] <= box_in.bbox[1],
            box_out.bbox[3] >= box_in.bbox[3]]):
        return True
    return False


class PdfBoxProcessor(list):
    '''
        Parse a PDF file to extract all the boxes including:
        text, curve, figure and line boxes
    '''
    def __init__(self, pdf_file):

        with open(str(pdf_file), 'rb') as document:
            # Create resource manager
            rsrcmgr = PDFResourceManager()

            # Set parameters for analysis.
            laparams = LAParams()

            # Create a PDF page aggregator object.
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(document):
                interpreter.process_page(page)

                # receive the LTPage object for the page.
                layout = device.get_result()
                for idx, element in enumerate(layout):
                    self.append(element)

    def get_box_type(self, BoxType) -> List:
        return [box for box in self if isinstance(box, BoxType)]

    def get_box_text(self) -> List:
        return self.get_box_type(LTTextBoxHorizontal)

    def get_box_curve(self) -> List:
        return self.get_box_type(LTCurve)

    def get_box_figure(self) -> List:
        return self.get_box_type(LTFigure)

    def get_box_line(self) -> List:
        return self.get_box_type(LTLine)


def sort_box_horizontal(box_list: List, reverse=False) -> List:
    return sorted(box_list, reverse=reverse, key=lambda item: item.bbox[0])


def sort_box_vertical(box_list: List, reverse=False) -> List:
    return sorted(box_list, reverse=reverse, key=lambda item: item.bbox[1])


JobPath = namedtuple(
    'JobPath', 'file_name job_class_title, x0 y0 x1 y1')


def get_job_paths_in_file(job_path_file: pathlib.Path) -> List:
    ' parse a job path pdf file to extract job paths in boxes '
    boxes = PdfBoxProcessor(job_path_file)
    text_list = boxes.get_box_text()

    figure_list = sort_box_vertical(boxes.get_box_figure(), reverse=True)

    job_paths = []
    for figure in figure_list:

        job_text_list = []
        for text in text_list:
            if is_in_box(text, figure):
                job_text = text.get_text().replace('\n', ' ').strip()
                job_text_list.append(' '.join(job_text.split()))

        job_title = ' '.join(job_text_list)

        job_path = JobPath(
            job_path_file.name, job_title,
            figure.x0, figure.y0, figure.x1, figure.y1)

        job_paths.append(job_path)

    return job_paths


def get_job_paths(paths: List[pathlib.Path]):
    ' gets a data frame of job paths from a list of job paths pdf files '
    job_paths_list: List = []
    for path in paths:
        job_paths = get_job_paths_in_file(path)
        log.info('File {}, jobs {}'.format(path.name, len(job_paths)))
        job_paths_list.extend(job_paths)
    df = pd.DataFrame(data=job_paths_list, columns=JobPath._fields)
    return df
