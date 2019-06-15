from typing import List


class _Lex:
    def __init__(self, json): self.json = json

    def lemma(self) -> str: return self.json["lemma"]

    def base(self) -> str: return self.json["base"]

    def pos(self) -> str: return self.json["pos"]

    def labels(self) -> List[str]: return self.json["labels"]

    def flexions(self) -> List['_Lex']: return list(self.json["flexions"])

    def hyperonyms(self) -> List['_Lex']: return list(self.json["hyperonyms"])

    def meronyms(self) -> List['_Lex']: return list(self.json["meronyms"])

    def synonyms(self) -> List['_Lex']: return list(self.json["synonyms"])

    def abbreviations(self) -> List['_Lex']: return list(self.json["abbreviations"])

    def causations(self) -> List['_Lex']: return list(self.json["causations"])

    def collocations(self) -> List['_Lex']: return list(self.json["collocations"])

    def parts(self) -> List['_Lex']: return list(self.json["parts"])


class _Dep:
    def __init__(self, json): self.json = json

    def source(self) -> str: return self.json["source"]

    def target(self) -> str: return self.json["target"]

    def sourcePos(self) -> str: return self.json["sourcePos"]

    def targetPos(self) -> str: return self.json["targetPos"]

    def sourceTag(self) -> str: return self.json["sourceTag"]

    def targetTag(self) -> str: return self.json["targetTag"]

    def sourceIndex(self) -> int: return self.json["sourceIndex"]

    def targetIndex(self) -> int: return self.json["targetIndex"]

    def sourceBase(self) -> str: return self.json["sourceBase"]

    def targetBase(self) -> str: return self.json["targetBase"]

    def relation(self) -> str: return self.json["relation"]

    def rawRelation(self) -> str: return self.json["rawRelation"]


class _Ner:
    def __init__(self, json): self.json = json

    def custom(self) -> List['_Custom']: return self.json["custom"]


class _Custom:
    def __init__(self, json): self.json = json

    def data(self) -> {}: return self.json["data"]

    def negation(self) -> bool: return self.json["negation"]

    def indices(self) -> [int]: return self.json["indices"]


class _Nlu:
    def __init__(self, json): self.json = json

    def txt(self) -> str: return self.json["txt"]

    def raw(self) -> str: return self.json["raw"]

    def cls(self) -> str: return self.json["cls"]

    def lex(self) -> List[_Lex]: return list(map(lambda x: _Lex(x), list(self.json["lex"])))

    def dep(self) -> List[_Dep]: return list(map(lambda x: _Dep(x), list(self.json["dep"])))

    def ner(self) -> List[_Ner]: return list(map(lambda x: _Ner(x), list(self.json["ner"])))


class _Data:
    def __init__(self, json): self.json = json

    def nlu(self) -> List[_Nlu]: return list(map(lambda x: _Nlu(x), list(self.json["nlu"])))

    def ver(self) -> str: return self.json["ver"]


class AtlasResponse:
    """
    Response dto used by the AtlasClient.
    """

    def __init__(self, json): self.json = json

    def ner_score(self) -> float: return self.json["nerScore"]

    def score(self) -> float: return self.json["score"]

    def nlu_score(self) -> float: return self.json["nluScore"]

    def data(self) -> _Data: return _Data(self.json["data"])

    def logs(self) -> {}: return self.json["logs"]

    def errors(self) -> List[str]: return list(self.json["errors"])
