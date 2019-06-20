import os
import spacy
import majka

from ufal.morphodita import Tagger
from gherkan.utils import constants as c


class NLPModelManager:

    def __init__(self):
        self.nlp_model_en = None
        self.nlp_model_cs = None
        self.morph_lwt = None
        self.morph_wlt = None

        self.nlp_model_cs_path = os.path.join(c.GHERKAN_ROOT_DIR, "morphodita", "czech-morfflex-pdt-161115",
                                   "czech-morfflex-pdt-161115.tagger")

        self.morph_lwt_path = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "majka.l-wt")
        self.morph_wlt_path = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "majka.w-lt")


    def load_all_models(self):
        self.nlp_model_en = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner'])
        self.nlp_model_cs = Tagger.load(self.nlp_model_cs_path)

        self.morph_lwt = majka.Majka(self.morph_lwt_path)
        self.morph_wlt = majka.Majka(self.morph_wlt_path)