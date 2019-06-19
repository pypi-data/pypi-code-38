from .doc_collection import DocumentCollection

# Документ с привязанным к нему объектом
class TaggedDocument():
    def __init__(self, document:[], doc_tags:[]):
        self.doc = document
        self.tags = doc_tags

# Коллекция документов с привязанным к документу объектом (tags)
class TaggedDocumentCollection(DocumentCollection):
    def __init__(self, tagged_documents:[TaggedDocument]=None):
        super().__init__(tagged_documents)