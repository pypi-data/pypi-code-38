from typing import Callable


class _Lex(list):

    def lemma(self):
        self.append("lemma")
        return self

    def base(self):
        self.append("base")
        return self

    def pos(self):
        self.append("pos")
        return self

    def flexions(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("flexions { " + (" ".join(lex)) + " }")
        return self

    def hyperonyms(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("hyperonyms { " + (" ".join(lex)) + " }")
        return self

    def meronyms(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("meronyms { " + (" ".join(lex)) + " }")
        return self

    def parts(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("parts { " + (" ".join(lex)) + " }")
        return self

    def labels(self):
        self.append("labels")
        return self

    def synonyms(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("synonyms { " + (" ".join(lex)) + " }")
        return self

    def abbreviations(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("abbreviations { " + (" ".join(lex)) + " }")
        return self

    def causations(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("causations { " + (" ".join(lex)) + " }")
        return self

    def collocations(self, callback: Callable[['_Lex'], None]):
        lex = _Lex()
        callback(lex)
        self.append("collocations { " + (" ".join(lex)) + " }")
        return self


class _Dep(list):
    def source(self): self.append("source")

    def target(self): self.append("target")

    def sourcePos(self): return self.append("sourcePos")

    def targetPos(self): return self.append("targetPos")

    def sourceTag(self): return self.append("sourceTag")

    def targetTag(self): return self.append("targetTag")

    def sourceIndex(self): return self.append("sourceIndex")

    def targetIndex(self): return self.append("targetIndex")

    def sourceBase(self): return self.append("sourceBase")

    def targetBase(self): return self.append("targetBase")

    def relation(self): return self.append("relation")

    def rawRelation(self): return self.append("rawRelation")


class _Ner(list):
    def custom(self, qualifier, callback: Callable[['_Custom'], None]):
        custom = _Custom()
        callback(custom)
        self.append("custom(qualifier:\"" + qualifier + "\") {" + (" ".join(custom)) + " }")
        return self


class _Custom(list):
    def data(self): self.append("data")

    def negation(self): self.append("negation")

    def indices(self): self.append("indices")


class AtlasRequest(list):
    """
    Request DTO used by the AtlasClient.
    """

    @staticmethod
    def create(text: str, merge: bool = False):
        return AtlasRequest(text, merge)

    def __init__(self, text: str, merge: bool):
        super().__init__()
        self.text = text
        self.merge = merge

    def txt(self):
        self.append("txt")
        return self

    def raw(self):
        self.append("raw")
        return self

    def cls(self):
        self.append("cls")
        return self

    def lex(self, callback: Callable[[_Lex], None]):
        lex = _Lex()
        callback(lex)
        self.append("lex { " + (" ".join(lex)) + " }")
        return self

    def dep(self, callback: Callable[[_Dep], None]):
        dep = _Dep()
        callback(dep)
        self.append("dep { " + (" ".join(dep)) + " }")
        return self

    def ner(self, callback: Callable[[_Ner], None]):
        ner = _Ner()
        callback(ner)
        self.append("ner { " + (" ".join(ner)) + " }")
        return self
