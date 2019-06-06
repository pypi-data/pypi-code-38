import random
from pathlib import Path
from unittest import TestCase

from sekg.ir.doc.wrapper import MultiFieldDocumentCollection
from sekg.ir.preprocessor.code_text import CodeDocPreprocessor
from test.data.definition import ROOT_DIR


class TestCodeDocPreprocessor(TestCase):
    def test_clean(self):
        data_dir = Path(ROOT_DIR)

        preprossor = CodeDocPreprocessor()
        doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(
            str(data_dir / "JabRef-2.6.v3.sub.dc"))

        chosen_indexs = list(range(0, doc_collection.get_num()))
        random.shuffle(chosen_indexs)
        chosen_indexs = chosen_indexs[:50]
        for index in chosen_indexs:
            doc = doc_collection.get_by_index(index=index)
            text = doc.get_document_text()
            print("old text=", text)
            print("------------")
            clean = preprossor.clean(text=text)
            print("clean text=", " ".join(clean))
            print("------------\n\n")
