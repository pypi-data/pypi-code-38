
__version__ = "2019.06.05.1"


import os.path as op
from .genannot import annotate_pdf
from .extractannot import pdfannot2df

exple_pdf = op.join(op.dirname(__file__), 'test_ressources/pdf_without_annot.pdf')