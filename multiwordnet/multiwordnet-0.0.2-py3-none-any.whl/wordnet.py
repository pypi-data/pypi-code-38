"""
A helper library for accessing and manipulating WordNets within the MultiWordNet.
"""

import re
from collections import deque
from functools import lru_cache
from sqlite3 import OperationalError
from typing import Generator, Iterable, List, Tuple

from multiwordnet.db import connect as db


class POSError(Exception):
    pass


class Semfield(object):
    """
    Represents a semfield (semantic field) within the MultiWordNet.

    english: A descriptive name of the semfield in English.
    code: A unique identification code.
    synsets: A list of synset identification numbers falling within this semantic field.
    normal: The semfield that represents the basic category to which this semfield belongs.
    hypers: A list of semfields immediately superordinate to this semfield.
    hypons: A list of semfields immediately subordinate to this semfield.
    """

    def __new__(cls, english, code=None, language='common'):
        english = english.replace(' ', '_')
        try:
            common_semfield_hierarchy = db("common", "semfield_hierarchy")

            if code:
                query = f'english="{english}" AND code="{code}"'
            else:
                query = f'english="{english}"'

            if common_semfield_hierarchy:
                common_semfield_hierarchy.execute(f'SELECT code, english FROM semfield_hierarchy WHERE {query}')
                results = common_semfield_hierarchy.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if not results:
                instance = None
            else:
                if len(results) > 1 and code is None:
                        results_codes = list()
                        for result in results:
                            results_codes.append(result[0])
                        raise ValueError(f'cannot disambiguate "{english}" between "{", ".join(results_codes)}"')
                else:
                    instance = super().__new__(cls)
                    instance._code = results[0][0]
                    instance._english = results[0][1]
                    instance._language = language
            return instance

    def __init__(self, english, code=None, language='common'):
        self._english = english
        self._code = code
        self._language = language
        self._synsets = None
        self._normal = None
        self._hypers = None
        self._hypons = None

    @property
    def language(self) -> str:
        return str(self._language)

    @property
    def synsets(self) -> List['Synset']:
        if not self._synsets:
            temp = list()
            try:
                common_semfield = db("common", "semfield")

                if common_semfield:
                    common_semfield.execute(f'SELECT synset FROM semfield WHERE english LIKE "%{self._english}%"')
                    common_results = common_semfield.fetchall()
                else:
                    common_results = None
            except OperationalError:
                raise
            else:
                if common_results:
                    for result in common_results:
                        temp.append(Synset(result[0], self.language))
            try:
                language_semfield = db(self.language, "semfield")

                if language_semfield:
                    language_semfield.execute(f'SELECT synset FROM semfield WHERE english LIKE "%{self._english}%"')
                    language_results = language_semfield.fetchall()
                else:
                    language_results = None
            except OperationalError:
                raise
            else:
                if language_results:
                    for result in language_results:
                        temp.append(Synset(result[0], self.language))
            self._synsets = temp
        return list(self._synsets)

    @property
    def hypers(self) -> List['Semfield']:
        if not self._hypers:
            temp = list()
            try:
                semfield_hierarchy = db("common", "semfield_hierarchy")

                if semfield_hierarchy:
                    semfield_hierarchy.execute(f'SELECT hypers FROM semfield_hierarchy WHERE english="{self._english}" AND code="{self.code}"')
                    result = semfield_hierarchy.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    for hyper in result[0].split(' '):
                        if hyper and hyper != '':
                            semfield_hierarchy.execute(f'SELECT code, english FROM semfield_hierarchy WHERE english="{hyper}"')  # AND code LIKE "{self.code[:2]}%"')
                            result = semfield_hierarchy.fetchone()

                            if result:
                                temp.append(Semfield(code=result[0], english=result[1], language=self.language))
            self._hypers = temp
        return list(self._hypers)

    @property
    def hypons(self) -> List['Semfield']:
        if not self._hypons:
            temp = list()
            try:
                semfield_hierarchy = db("common", "semfield_hierarchy")

                if semfield_hierarchy:
                    semfield_hierarchy.execute(f'SELECT hypons FROM semfield_hierarchy WHERE english="{self._english}" AND code="{self.code}"')
                    result = semfield_hierarchy.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    for hypon in result[0].split(' '):
                        if hypon is not None and hypon != '':
                            semfield_hierarchy.execute(f'SELECT code, english FROM semfield_hierarchy WHERE english="{hypon}"')  # AND code LIKE "{self.code[:3]}%"')
                            result = semfield_hierarchy.fetchone()

                            if result:
                                temp.append(Semfield(code=result[0], english=result[1], language=self.language))
            self._hypons = temp
        return list(self._hypons)

    @property
    def normal(self) -> 'Semfield':
        if not self._normal:
            try:
                semfield_hierarchy = db("common", "semfield_hierarchy")

                if semfield_hierarchy:
                    semfield_hierarchy.execute(f'SELECT normal FROM semfield_hierarchy WHERE english="{self._english}" AND code="{self.code}"')
                    result = semfield_hierarchy.fetchone()
                else:
                    result = None
            except OperationalError:
                    raise
            else:
                if result:
                    semfield_hierarchy.execute(f'SELECT code, english FROM semfield_hierarchy WHERE english="{result[0]}" AND code LIKE "{self.code[:2]}%"')
                    result = semfield_hierarchy.fetchone()

                    if result:
                        self._normal = Semfield(code=result[0], english=result[1], language=self.language)
        return self._normal

    @property
    def code(self) -> str:
        if not self._code:
            try:
                semfield_hierarchy = db("common", "semfield_hierarchy")

                if semfield_hierarchy:
                    semfield_hierarchy.execute(f"SELECT code FROM semfield_hierarchy WHERE english='{self._english}'")
                    result = semfield_hierarchy.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result and result[0]:
                    self._code = result[0]
        return str(self._code) if self._code else ''

    @property
    def english(self) -> str:
        return str(self._english)

    def __str__(self):
        return self._english.replace('_', ' ').title()

    def __repr__(self):
        return f"Semfield('{self.english}', '{self.code}')"


class Synset(object):
    """
    Represents a synset in a WordNet within the MultiWordNet.

    id: A unique identifier consisting of a part-of-speech tag ('n', 'v', 'a', or 'r') followed by # and an
         eight-digit offset number. For synsets of languages other than English, the first digit is typically
         an identifying character, but usage is not consistent across the MultiWordNet.
    language: The language of the WordNet instance to which the synset belongs.
    synset_language: The language for which the synset was originally defined.
    lemmas: A list of lemmas belonging to this synset in the given language.
    phrase: A list of phrases belonging to this synset in the given language.
    gloss: A gloss of the sense in English or in the language for which the synset was originally defined.
    """

    def __new__(cls, id: str, language: str):
        if id and language:
            try:
                result = None
                language_synset = db(cls.get_synset_language(id), "synset")

                if language_synset:
                    language_synset.execute(f"SELECT * FROM {cls.get_synset_language(id)}_synset WHERE id='{id}'")
                    result = language_synset.fetchone()
                if not result:
                    language_synset = db(language, "synset")
                    if language_synset:
                        language_synset.execute(f"SELECT * FROM {language}_synset WHERE id='{id}'")
                        result = language_synset.fetchone()
                if not result:
                    english_synset = db("english", "synset")
                    if english_synset:
                        english_synset.execute(f"SELECT * FROM english_synset WHERE id='{id}'")
                        result = english_synset.fetchone()
            except OperationalError:
                raise
            else:
                if result:
                    instance = super().__new__(cls)
                else:
                    instance = None
            return instance

    def __init__(self, id, language):
        self._id = id
        self._language = language
        self._relations = None
        self._semfield = None
        self._pos = None
        self._word = None
        self._phrase = None
        self._gloss = None

    @property
    def pos(self) -> str:
        if self._pos is None:
            self._pos = self.id[0]
        return str(self._pos)

    @property
    def offset(self) -> str:
        return str(self.id[2:])

    def get_relations(self, type: str) -> Generator['Relation', None, Iterable['Relation']]:
        if type in Relation.types[self.pos]:
            return (relation for relation in self.relations if relation.type == type)
        else:
            raise ValueError(f"No relation type '{type}' for '{self.pos}'!")

    @property
    def relations(self) -> List['Relation']:
        if not self._relations:
            temp = list()
            try:
                common_relation = db("common", "relation")

                if common_relation:
                    common_relation.execute(f"SELECT * FROM common_relation WHERE id_source='{self.id}'")
                    results = common_relation.fetchall()

                    if results:
                        for result in results:
                            temp.append(Relation(result[0], result[1], result[2], result[3]))

                language_relation = db(self.language, "relation")

                if language_relation:
                    language_relation.execute(f"SELECT * FROM {self.language}_relation WHERE id_source='{self.id}'")
                    results = language_relation.fetchall()

                    if results:
                        for result in results:
                            temp.append(Relation(result[0], result[1], result[2], result[3]))
            except OperationalError:
                raise
            else:
                self._relations = temp
        return list(self._relations)

    def relation_to(self, target: 'Synset') -> str:
        for relation in self.relations:
                if relation.target == target:
                    return relation.type

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def language(self) -> str:
        return str(self._language)

    @classmethod
    def get_synset_language(cls, id: str) -> str:
        """Returns the verbose language name for a given synset.

        :param id: A string of the form [pos#offset] identifying the synset.
        :return: The language name as a string.
        """
        if id:
            _language_names = {
                'P': 'english',  # Portuguese
                'N': 'italian',
                'W': 'italian',  # English
                'Y': 'italian',
                'H': 'hebrew',
                'S': 'spanish',
                'L': 'latin',
                'R': 'romanian',
            }
            if id[2].isdigit():
                return 'english'
            else:
                return _language_names[id[2]]

    @property
    def semfield(self) -> List['Semfield']:
        if not self._semfield:
            temp = list()
            try:
                common_semfield = db("common", "semfield")

                if common_semfield:
                    common_semfield.execute(f"SELECT english FROM semfield WHERE synset='{self.id}'")
                    result = common_semfield.fetchone()

                    if result:
                        for s in result[0].split(' '):
                            temp.append(Semfield(english=s, language=self.language))
                    else:
                        language_semfield = db(self.language, "semfield")

                        if language_semfield:
                            language_semfield.execute(f"SELECT english FROM {self.language}_semfield WHERE synset='{self.id}'")
                            result = language_semfield.fetchone()

                            if result:
                                for s in result[0].split(' '):
                                    self._semfield.append(Semfield(english=s, language=self.language))
            except OperationalError:
                raise
            else:
                self._semfield = temp
        return list(self._semfield)

    @property
    def lemmas(self) -> List['Lemma']:
        if not self._word:
            temp = list()
            _DB_COLUMN = {
                'n': 'id_n',
                'v': 'id_v',
                'a': 'id_a',
                'r': 'id_r',
            }

            try:
                language_synset = db(self.language, "synset")

                if language_synset:
                    language_synset.execute(f"SELECT word FROM {self.language}_synset WHERE id='{self.id}'")
                    result = language_synset.fetchone()

                    if result:
                        if result[0] and result[0] != ' GAP! ':
                            temp = [Lemma(lemma, self.id[0], self.language) for lemma in result[0].strip().split(' ')]
                else:
                    language_index = db(self.language, "index")

                    if language_index:
                        language_index.execute(f"SELECT lemma FROM {self.language}_index WHERE {_DB_COLUMN[self.pos]} LIKE '%{self.id}%';")
                        results = language_index.fetchall()

                        if results:
                            for result in results:
                                if result[0] != 'gap!':
                                    temp.append(Lemma(result[0], self.id[0], self.language))
            except OperationalError:
                raise
            else:
                self._word = temp
        return list(self._word)

    @property
    def gloss(self) -> str:
        if not self._gloss:
            try:
                language_synset = db(self.get_synset_language(self.id), "synset")

                if language_synset:
                    language_synset.execute(f"SELECT gloss FROM {self.get_synset_language(self.id)}_synset WHERE id='{self.id}'")
                    result = language_synset.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    self._gloss = result[0]
        return str(self._gloss) if self._gloss else ''

    def __hash__(self):
        return hash((self.pos, self.offset))

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return str(self.gloss)

    def __repr__(self):
        return f"Synset('{self.id}', '{self.get_synset_language(self.id)}')"


    @property
    def root(self):
        """Get the topmost hypernyms of this synset. """

        result = []
        seen = set()
        todo = [self]
        while todo:
            next_synset = todo.pop()
            if next_synset not in seen:
                seen.add(next_synset)
                next_hypernyms = [relation.target
                                  for relation in next_synset.get_relations('@')]
                if not next_hypernyms:
                    result.append(next_synset)
                else:
                    todo.extend(next_hypernyms)
        return result

    def max_depth(self, path: list = None):
        """
        :return: The length of the longest hypernym path from this
        synset to the root.
        """

        if path is None:
            path = []

        if len(path) > 1 and self in path[1:]:
            return 0
        else:
            path.append(self)
            hypernyms = [hypernymy.target for hypernymy in self.get_relations('@')]
            if len(hypernyms) == 0:
                return 0
            else:
                return 1 + max(hypernym.max_depth(path) for hypernym in hypernyms)

    @property
    def min_depth(self, path: list = None):
        """
        :return: The length of the shortest hypernym path from this
        synset to the root.
        """

        if path is None:
            path = []

        if len(path) > 1 and self in path[1:]:
            return 0
        else:
            path.append(self)
            hypernyms = [hypernymy.target for hypernymy in self.get_relations('@')]
            if len(hypernyms) == 0:
                return 0
            else:
                return 1 + min(hypernym.min_depth(path) for hypernym in hypernyms)

    @property
    def closure(self, type: str, depth=-1):
        """Return the transitive closure of synset under the
        relationship of type 'type', breadth-first
        """
        ids = []
        for target in breadth_first(list(self.get_relations(type)), depth):
            if target.id != self.id:
                if target.id not in ids:
                    ids.append(target.id)
                    yield target

    @property
    def paths_to_root(self):
        """
        Get the path(s) from synset to the root, where each path is a
        list of the synset nodes traversed on the way to the root.

        :return: A list of lists, where each list gives the node sequence
           connecting the initial ``Synset`` node and a root node.
        """
        paths = []

        hypernyms = list(self.get_relations('@'))
        if len(hypernyms) == 0:
            paths = [[self]]

        for hypernym in hypernyms:
            for ancestor_list in hypernym.target.paths_to_root:
                ancestor_list.append(self)
                paths.append(ancestor_list)
        return paths


class Morpho(object):
    """ Represents morphological information for a Lemma in the WordNet """
    def __init__(self, fields, language):
        if language == 'hebrew':
            self._id, self._lemma, self._pos, self._principal_parts, self._irregular_forms, \
            self._alternative_forms, self._pronunciation, self._undotted, self._dotted_without_dots, \
            self._variants, self._translit_dotted, self._translit_undotted, self._miscellanea = fields
            self._language = language
        elif language == 'latin':
            self._id, self._lemma, self._pos, self._principal_parts, self._irregular_forms, \
            self._alternative_forms, self._pronunciation, self._miscellanea = fields
            self._language = language

    @property
    def language(self) -> str:
        return str(self._language)

    @property
    def lemma(self) -> str:
        return str(self._lemma)

    @property
    def lemma_verbose(self) -> str:
        if self.language == 'latin':
            i = self._lemma
            if self.pos == 'v':
                if len(self.principal_parts) == 3:
                    if self.group == '1': thematic_vowel = 'a'
                    elif self.group == '2': thematic_vowel = 'e'
                    elif self.group == '3': thematic_vowel = 'e'
                    else: thematic_vowel = 'i'
                    if self.voice == 'a':
                        ii = f"{self.principal_parts[0]}{thematic_vowel}re"
                        iii = f"{self.principal_parts[1]}isse"
                        iv = f"{self.principal_parts[2]}um"
                        _lemma = list((i, ii, iii, iv, self.group))
                    else:
                        ii = f"{self.principal_parts[0]}{thematic_vowel}ri"
                        iii = f"{self.principal_parts[2]}us sum"
                        _lemma = list((i, ii, iii, self.group))
                elif len(self.principal_parts) == 2:
                    ii = f"{self.principal_parts[0]}isse"
                    iii = f"{self.principal_parts[1]}"
                    _lemma = list((i, ii, iii, self.group))
            elif self.pos == 'n':
                if self.group == '1': genitive = 'ae' if self.number == 's' else "arum"
                elif self.group == '2': genitive = 'i' if self.number == 's' else "orum"
                elif self.group == '3': genitive = 'is' if self.number == 's' else "um"
                elif self.group == '4': genitive = 'us' if self.number == 's' else "uum"
                else: genitive = 'ēi' if self.number == 's' else "erum"
                ii = f"{self.principal_parts[0]}{genitive}"
                _lemma = list((i, ii, f"{self.gender}."))
            elif self.pos == 'a':
                if self.group == '1':
                    ii = f"{self.principal_parts[0]}a"
                    iii = f"{self.principal_parts[0]}um"
                    _lemma = list((i, ii, iii))
                elif self.group == '3':
                    if self.gender == 'm': # 3-termination
                        ii = f"{self.principal_parts[0]}is"
                        iii = f"{self.principal_parts[0]}e"
                        _lemma = list((i, ii, iii, 'm.f.n.'))
                    elif self.gender == 'c': # 2-termination
                        ii = f"{self.principal_parts[0]}e"
                        _lemma = list((i, ii, 'mf.n.'))
                    elif self.gender == 'a': # 1-termination
                        _lemma = list((i, 'mfn.'))
                elif self.pos == 'r':
                    if self.principal_parts:
                        _lemma = list((self._lemma, self.principal_parts[0], self.principal_parts[1]))
        else:
            _lemma = self._lemma
        return _lemma

    @property
    def id(self) -> str:
        if not self._id:
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT id FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    self._id = result[0]
        return str(self._id) if self._id else ''

    @property
    def irregular_forms(self) -> dict:
        if not self._irregular_forms:
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT irregular_forms FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result and result[0]:
                    self._irregular_forms = result[0]
        return [tuple(irregular_form.split('=')) for irregular_form in self._irregular_forms.strip().split(' ')] if self._irregular_forms else []

    @property
    def alternative_forms(self) -> dict:
        if not self._alternative_forms:
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT alternative_forms FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result and result[0]:
                    self._alternative_forms = result[0]
        return [tuple(alternative_form.split('=')) for alternative_form in self._alternative_forms.strip().split(' ')] if self._alternative_forms else []

    @property
    def principal_parts(self) -> List[str]:
        if not self._principal_parts:
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT principal_parts FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result and result[0]:
                    self._principal_parts = result[0]
        return self._principal_parts.strip().split(' ') if self._principal_parts else []

    @property
    def pronunciation(self) -> str:
        if not self._pronunciation:
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT pronunciation FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    self._pronunciation = result[0]
        return str(self._pronunciation) if self._pronunciation else ''

    @property
    def undotted(self) -> str:
        if self.language == 'hebrew':
            if not self._undotted:
                try:
                    language_morpho = db(self.language, "morpho")
                    language_morpho.execute(f"SELECT undotted FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                except OperationalError:
                    raise
                else:
                    if result:
                        self._undotted = result[0]
        return str(self._undotted) if self._undotted else ''

    @property
    def dotted_without_dots(self) -> str:
        if self.language == 'hebrew':
            if not self._dotted_without_dots:
                try:
                    language_morpho = db(self.language, "morpho")
                    language_morpho.execute(f"SELECT dotted_without_dots FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                except OperationalError:
                    raise
                else:
                    if result:
                        self._dotted_without_dots = result[0]
        return str(self._dotted_without_dots) if self._dotted_without_dots else ''

    @property
    def variants(self) -> str:
        if self.language == 'hebrew':
            if not self._variants:
                try:
                    language_morpho = db(self.language, "morpho")
                    language_morpho.execute(f"SELECT variants FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                except OperationalError:
                    raise
                else:
                    if result:
                        self._variants = result[0]
        return str(self._variants) if self._variants else ''

    @property
    def translit_dotted(self) -> str:
        if self.language == 'hebrew':
            if not self._translit_dotted:
                try:
                    language_morpho = db(self.language, "morpho")
                    language_morpho.execute(f"SELECT translit_dotted FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                except OperationalError:
                    raise
                else:
                    if result:
                        self._translit_dotted = result[0]
        return str(self._translit_dotted) if self._translit_dotted else ''

    @property
    def translit_undotted(self) -> str:
        if self.language == 'hebrew':
            if not self._translit_undotted:
                try:
                    language_morpho = db(self.language, "morpho")
                    language_morpho.execute(f"SELECT translit_undotted FROM {self.language}_morpho WHERE lemma='{self.lemma}' and pos='{self.pos}';")
                    result = language_morpho.fetchone()
                except OperationalError:
                    raise
                else:
                    if result:
                        self._translit_undotted = result[0]
        return str(self._translit_undotted) if self._translit_undotted else ''

    @property
    def miscellanea(self) -> str:
        if not self._miscellanea:
            temp = ''
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT miscellanea FROM {self._language}_morpho WHERE lemma='{self._lemma}' and pos='{self._pos}';")
                    result = language_morpho.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if result:
                    temp = result[0]
            self._miscellanea = temp
        return str(self._miscellanea)

    @property
    def pos(self) -> str:
        if not self._pos:
            groups = re.search(r'^([nvarpusct])[\S][\S][\S][\S][\S][\S][\S][\S][\S]$', self.miscellanea)
            self._pos = groups.group(1) if groups else ''
        return str(self._pos) if self._pos else ''

    @property
    def pos_verbose(self) -> str:
        _pos_types = {
            'n': 'noun',
            'v': 'verb',
            'a': 'adjective',
            'r': 'adverb',  # = 'r'
            'p': 'pronoun',
            'u': 'punctuation',
            's': 'preposition',
            'c': 'conjunction',
            't': 'participle',
        }
        return str(_pos_types[self.pos])

    @property
    def person(self) -> str:
        if self.pos == 'v':
            groups = re.search(r'^[\S]([123])[\S][\S][\S][\S][\S][\S][\S][\S]$', self.miscellanea)
            return groups.group(1) if groups else ''
        else:
            return None

    @property
    def person_verbose(self) -> str:
        if self.pos == 'v':
            _person_types = {
                '1': '1st person',
                '2': '2nd person',
                '3': '3rd person',
            }
            return str(_person_types[self.person])
        else:
            return None

    @property
    def degree(self) -> str:
        if self.pos == 'a' or self.pos == 'r':
            groups = re.search(r'^[\S]([pcs])[\S][\S][\S][\S][\S][\S][\S][\S]$', self.miscellanea)
            return groups.group(1) if groups else ''
        else:
            return None

    @property
    def degree_verbose(self) -> str:
        if self.pos == 'a' or self.pos == 'r':
            _degree_types = {
                'p': 'positive',
                'c': 'comparative',
                's': 'superlative',
            }
            return str(_degree_types[self.degree])
        else:
            return None

    @property
    def number(self) -> str:
        groups = re.search(r'^[\S][\S]([sp])[\S][\S][\S][\S][\S][\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def number_verbose(self) -> str:
        _number_types = {
            's': 'singular',
            'd': 'dual',
            'p': 'plural',
        }
        return str(_number_types[self.number])

    @property
    def tense(self) -> str:
        groups = re.search(r'^[\S][\S][\S]([pfirlt])[\S][\S][\S][\S][\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def tense_verbose(self) -> str:
        _tense_types = {
            'p': 'present',
            'f': 'future',
            'i': 'imperfect',
            'r': 'perfect',
            'l': 'pluperfect',
            't': 'future perfect',
            }
        return str(_tense_types[self.tense])

    @property
    def mood(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S]([nimspgd])[\S][\S][\S][\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def mood_verbose(self) -> str:
        _mood_types = {
            'n': 'infinitive',
            'i': 'indicative',
            'm': 'imperative',  # ?
            's': 'subjunctive',
            'p': 'participle',   # ?
            'g': 'gerund',
            'd': 'gerundive',   # ?
        }
        return str(_mood_types[self.mood])

    @property
    def voice(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S]([apmds])[\S][\S][\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def voice_verbose(self) -> str:
        _voice_types = {
            'a': 'active',
            'p': 'passive',  # ?
            'm': 'middle',  # ?
            'd': 'deponent',
            's': 'semideponent'
        }
        return str(_voice_types[self.voice])

    @property
    def gender(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S]([mfnca])[\S][\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def gender_verbose(self) -> str:
        _gender_types = {
            'm': 'masculine',
            'f': 'feminine',
            'n': 'neuter',
            'c': 'masculine or feminine',
            'a': 'masculine or feminine or neuter',
        }
        return str(_gender_types[self.gender])

    @property
    def case(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S][\S]([ngdabvl])[\S][\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def case_verbose(self) -> str:
        _case_types = {
            'n': 'nominative',
            'g': 'genitive',
            'd': 'dative',
            'a': 'accusative',
            'b': 'ablative',
            'v': 'vocative',  # ?
            'l': 'locative',  # ?
        }
        return str(_case_types[self.case])

    @property
    def group(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S][\S][\S]([\d-])[\S]$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def stem(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S][\S][\S][\S]([\w-])$', self.miscellanea)
        return groups.group(1) if groups else ''

    @property
    def group_verbose(self) -> str:
        _group_types = {
            'n': {
                    '1': '1st declension',
                    '2': '2nd declension',
                    '3': '3rd declension',
                    '4': '4th declension',
                    '5': '5th declension',
                    '-': 'indeclinable',
                    },
            'v': {
                    '1': '1st conjugation',
                    '2': '2nd conjugation',
                    '3': '3rd conjugation',
                    '4': '4th conjugation',
                    },
            'a': {
                    '1': '1st/2nd declension',
                    '3': '3rd declension',
                    },
        }
        return str(_group_types[self.pos][self.group])

    @property
    def is_istem(self) -> bool:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S][\S][\S][\S]([i])$', self.miscellanea)
        return True if groups else False

    @property
    def istem(self) -> str:
        groups = re.search(r'^[\S][\S][\S][\S][\S][\S][\S][\S][\S]([i-])$', self.miscellanea)
        return groups.group(1) if groups else ''

    def __repr__(self):
        return f"Morpho('{self.lemma}', '{self.pos}')"

    def __str__(self):
        return self.miscellanea


class Lemma(object):
    """Represents a Lemma in a WordNet within the MultiWordNet.

    _lemma: The dictionary form of the word.
    _language: The language of the WordNet to which the word belongs.
    _pos: The part of speech of the word.
    _synset: A Synset object representing a synonym set to which the word belongs.
    _synonyms: A list of Lemmas corresponding to the other members of the word's synsets.
    _phrase: 'Y' if the Lemma is a phrase
    """

    def __new__(cls, lemma, pos, miscellanea=None, id=None, language='english'):
        if "''" in lemma:
            pass
        elif "'" in lemma:
            lemma = lemma.replace("'", "''")
        if ' ' in lemma:
            lemma = lemma.replace(' ', '_')
        if language != 'latin':
            db_column = {
            'n': 'id_n',
            'v': 'id_v',
            'a': 'id_a',
            'r': 'id_r',
            '*': 'id_n, id_v, id_a, id_r',
            }
            try:
                language_index = db(language, "index")
                if language_index:
                    language_index.execute(f'SELECT {db_column[pos]} FROM {language}_index WHERE lemma="{lemma}"')
                    result = language_index.fetchone()
                else:
                    result = None
            except OperationalError:
                raise
            else:
                if not result or (pos in ('n', 'v', 'a', 'r') and not result[0]):
                    instance = None
                else:
                    if pos == '*':
                        resolved_pos = ''
                        if result[0]:
                            resolved_pos += 'n'
                        if result[1]:
                            resolved_pos += 'v'
                        if result[2]:
                            resolved_pos += 'a'
                        if result[3]:
                            resolved_pos += 'r'
                        if len(resolved_pos) > 1:
                            raise POSError(f"cannot disambiguate '{lemma}' between '{', '.join(resolved_pos)}'")
                        else:
                            pos = resolved_pos
                    instance = super().__new__(cls)
                    instance._lemma = lemma
                    instance._pos = pos
                return instance
        else:
            if miscellanea:
                mquery = f"miscellanea='{miscellanea}'"
            else:
                mquery = ''

            if id:
                iquery = f"id='{id}'"
            else:
                iquery = ''
            if pos in 'nvar':
                pquery = f"pos='{pos}'"
            else:
                pquery = ""
            query = ' AND '.join(filter(None, [iquery, pquery, mquery]))
            if query: query = ' AND ' + query
            try:
                language_morpho = db(language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT * FROM {language}_morpho WHERE lemma='{lemma}'{query};")
                    results = language_morpho.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if not results:
                    instance = None
                else:
                    if len(results) > 1:
                        ambig = ", ".join([result[1] for result in results])
                        raise ValueError(f"cannot disambiguate {lemma} between {ambig}; use get() instead")
                    else:
                        result = results[0]
                        instance = super().__new__(cls)
                        instance._lemma = result[1]
                        instance._pos = result[2]
                        instance._morpho = Morpho(result, language=language)
                return instance

    def __init__(self, lemma, pos, miscellanea, id, language):
        if pos != '*' and pos is not None:
            self._pos = pos
        self._lemma = lemma
        self._language = language
        self._synsets = None
        self._synonyms = None
        self._id = id

    @property
    def morpho(self) -> Morpho:
        if not self._morpho:
            self._morpho = Morpho(self.lemma, self.pos, self.language)
        return self._morpho if self._morpho else None

    @property
    def synsets(self) -> List['Synset']:
        if not self._synsets:
            temp = list()
            _DB_COLUMN = {
                    'n': 'id_n',
                    'v': 'id_v',
                    'a': 'id_a',
                    'r': 'id_r',
                    '*': 'id_n, id_v, id_a, id_r',
                }
            try:
                language_index = db(self.language, "index")

                if language_index:
                    language_index.execute(f"SELECT {_DB_COLUMN[self.pos]} FROM {self.language}_index WHERE lemma='{self.lemma}'")
                    result = language_index.fetchone()

                    if result:
                        if self.pos == '*':
                            if not result[0]:  # n
                                if not result[1]:  # v
                                    if not result[2]:  # a
                                        temp = [Synset(syn, self.language) for syn in result[3].split(' ') if syn]  # r
                                    else:
                                        temp = [Synset(syn, self.language) for syn in result[2].split(' ') if syn]
                                else:
                                    temp = [Synset(syn, self.language) for syn in result[1].split(' ') if syn]
                            else:
                                temp = [Synset(syn, self.language) for syn in result[0].split(' ') if syn]
                        elif result[0]:
                            temp = [Synset(syn, self.language) for syn in result[0].split(' ') if syn]
            except OperationalError:
                raise
            else:
                self._synsets = temp
        return list(self._synsets)

    @property
    def synonyms(self) -> list:
        if not self._synonyms:
            temp = set()
            try:
                language_synonyms = db(self.language, "synonyms")

                if language_synonyms:
                    for synset in self.synsets:
                        language_synonyms.execute(f"SELECT lemma FROM {self.language}_synonyms WHERE pos='{self.pos}' AND syn='{synset.offset}'")
                        results = language_synonyms.fetchall()
                        if results:
                            for result in results:
                                if result[0] != self.lemma:
                                    temp.add(Lemma(result[0], self.pos, self.language))

                if not temp:
                    language_synset = db(self.language, "synset")

                    if language_synset:
                        for synset in self.synsets:
                            language_synset.execute(f"SELECT word, phrase FROM {self.language}_synset WHERE id='{synset.id}'")
                            result = language_synset.fetchone()
                            if result[0]:
                                for word in result[0].strip().split(' '):
                                    if word != self.lemma:
                                        temp.add(Lemma(word, self.pos, self.language))
                            if result[1]:
                                for phrase in result[1].strip().split(' '):
                                    temp.add(Lemma(phrase, self.pos, self.language))
            except OperationalError:
                raise
            else:
                self._synonyms = list(temp)
        return list(self._synonyms)

    def __eq__(self, other):
        return self.lemma == other.lemma and self.pos == other.pos

    def __lt__(self, other):
        return self.lemma < other.lemma
        
    def __hash__(self):
        return hash((self.lemma, self.pos))

    @property
    def lemma(self) -> str:
        return str(self._lemma)

    @property
    def language(self) -> str:
        return str(self._language)

    @property
    def pos(self) -> str:
        return str(self._pos)

    def get_derivates(self, pos: str='nvar') -> List['Lemma']:
        """ Returns all Lemmas with Relation of type '\' (derived-from) to the Lemma matching part of speech 'pos' """

        _derived_words = [derivate for derivate in self.derivates if derivate.pos in pos]
        return _derived_words

    @property
    def derivates(self) -> List['Lemma']:
        """ Returns all Lemmas with Relation of type '\' (derived-from) to the Lemma """
        _derived_words = list()
        try:
            language_relation = db(self.language, "relation")
            language_relation.execute(f"SELECT id_source, w_source FROM {self.language}_relation WHERE w_target='{self.lemma}' AND type='\\';")
            results = language_relation.fetchall()
        except OperationalError:
            raise
        else:
            if results:
                for result in results:
                    _derived_words.append(Lemma(result[1], result[0][0], self.language))
            return _derived_words

    def get_relatives(self, pos: str='nvar') -> List['Lemma']:
        """ Returns all Lemmas with Relation of type '/' (related-to) to the Lemma matching part of speech 'pos' """

        _related_words = [relative for relative in self.relatives if relative.pos in pos]
        return _related_words

    @property
    def relatives(self) -> List['Lemma']:
        """ Returns all Lemmas with Relation of type '/' (related-to) to the Lemma """
        _related_words = list()
        try:
            language_relation = db(self.language, "relation")
            language_relation.execute(f"SELECT id_target, w_target FROM {self.language}_relation WHERE w_source='{self.lemma}' AND type='/';")
            results = language_relation.fetchall()
        except OperationalError:
            raise
        else:
            if results:
                for result in results:
                    _related_words.append(Lemma(result[1], result[0][0], self.language))

        return _related_words

    @property
    def antonyms(self) -> list:
        """ Returns all Lemmas with Relation of type '!' (antonym) """

        temp = set()
        try:
            language_relation = db(self.language, "relation")
            if language_relation:
                language_relation.execute(f"SELECT id_target, w_target FROM {self.language}_relation WHERE w_source='{self.lemma}' AND type='!';")
                results = language_relation.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if results:
                for result in results:
                    temp.add((result[1], result[0][0],))

        _antonyms = list()
        if temp:
            for antonym in temp:
                _antonyms.append(Lemma(*antonym, self.language))
        return _antonyms

    def __str__(self):
        return self._lemma.replace('_', ' ')

    def __repr__(self):
        return f"Lemma('{self.lemma}', '{self.pos}', '{self.language}')"


class Relation(object):
    """

    """

    types = {
        'n':
            {
                '!': 'antonym (lexical)',
                '@': 'hypernym',
                '~': 'hyponym',
                '#m': 'member-of',
                '#s': 'substance-of',
                '#p': 'part-of',
                '%m': 'has-member',
                '%s': 'has-substance',
                '%p': 'has-part',
                '=': 'attribute',
                '|': 'nearest',
                '+r': 'has-role',
                '-r': 'is-role-of',
                '+c': 'composed-of (lexical)',
                '-c': 'composes (lexical)',
                r'\\': 'derived-from (lexical)',  # NEW
                '/': 'related-to (lexical)',  # NEW
            },
        'v':
            {
                '!': 'antonym (lexical)',
                '@': 'hypernym',
                '~': 'hyponym',
                '*': 'entailment',
                '>': 'causes',
                '^': 'also-see',
                '$': 'verb-group',
                '|': 'nearest',
                '+c': 'composed-of (lexical)',
                '-c': 'composes (lexical)',
                r'\\': 'derived-from (lexical)',  # NEW
                '/': 'related-to (lexical)',  # NEW
            },
        'a':
            {
                '!': 'antonym (lexical)',
                '@': 'hypernym',
                '~': 'hyponym',
                '&': 'similar-to',
                '<': 'participle (lexical)',  # of a verb
                r'\\': 'pertains-to (lexical)',  # to a noun, equivalent to 'derived-from'
                '=': 'is-value-of',
                '^': 'also-see',
                '|': 'nearest',
                '+c': 'composed-of (lexical)',
                '-c': 'composes (lexical)',
                '/': 'related-to (lexical)',  # NEW
            },
        'r':
            {
                '!': 'antonym (lexical)',
                '@': 'hypernym',
                '~': 'hyponym',
                r'\\': 'derived-from (lexical)',
                '|': 'nearest',
                '+c': 'composed-of (lexical)',
                '-c': 'composes (lexical)',
                '/': 'related-to (lexical)',  # NEW
            },
    }

    def __init__(self, type: str, id_source: str, id_target: str, w_source: str=None, w_target: str=None, status: str=None, language: str='english'):
        self._type = type

        self._id_source = id_source
        self._id_target = id_target

        self._w_source = w_source
        self._w_target = w_target
        self._language = language

        if status in ('new', 'NEW'):
            self._status = status.lower()
        else:
            self._status = ''

    @property
    def language(self) -> str:
        return str(self._language)

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def type_verbose(self) -> str:
        if self._id_source[0] != 'n':
            if self._id_source[0] != 'v':
                if self._id_source[0] != 'a':
                    return self.types['r'][self._type]
                else:
                    return self.types['a'][self._type]
            else:
                return self.types['v'][self._type]
        else:
            return self.types['n'][self._type]

    @property
    def id_target(self) -> str:
        return str(self._id_target)

    @property
    def id_source(self) -> str:
        return str(self._id_source)

    @property
    def w_target(self) -> Lemma:
        return Lemma(self._w_target, self.target.pos, language=self.target.language, id=None, miscellanea=None) if self._w_target else None

    @property
    def w_source(self) -> Lemma:
        return Lemma(self._w_source, self.source.pos, language=self.source.language, id=None, miscellanea=None) if self._w_source else None

    @property
    def is_lexical(self) -> bool:
        return bool(isinstance(self.w_source, Lemma) and isinstance(self.w_target, Lemma))

    @property
    def status(self) -> str:
        return str(self._status)

    @property
    def source(self) -> Synset:
        return Synset(self.id_source, Synset.get_synset_language(self.id_target))

    @property
    def target(self) -> Synset:
        return Synset(self.id_target, Synset.get_synset_language(self.id_target))

    def __repr__(self):
        if self.is_lexical:
            return f"Relation('{self.type}', '{str(self.w_source)}', '{str(self.w_target)}')"
        else:
            return f"Relation('{self.type}', '{self.id_source}', '{self.id_target}')"

    def __str__(self):
        if self.is_lexical:
            return f"{str(self.w_source)} {self.type_verbose} {str(self.w_target)}"
        else:
            return f"{self.id_source} {self.type_verbose} {self.id_target}"


class WordNet(object):
    """
    Represents a WordNet within the MultiWordNet.

    _language: A string giving the name of the language of the WordNet. Default is 'english'.
    _relations: A list of Relation objects representing the semantic or lexical relations defined for the WordNet.
    _lemmas: A list of Lemma objects representing distinct lemmas within the WordNet.
    _synsets: A list of Synset objects representing the synsets defined for the WordNet.
    _semfields: A list of all semfields defined for the MultiWordNet.
    """

    def __init__(self, language: str='english'): # iso 639-3
        self._language = language
        self._relations = None
        self._lemmas = None
        self._synsets = None
        self._semfields = None

    @property
    def cache(self):
        return self._cache

    def get_synset(self, id: str) -> Synset:
        return Synset(id, self.language)

    @property
    def index(self):
        for lemma in self.lemmas:
            yield (lemma.lemma, lemma.pos, lemma.morpho.miscellanea)

    @property
    def language(self) -> str:
        return str(self._language)

    @property
    def synsets(self) -> Generator['Synset', None, Iterable['Synset']]:
        if not self._synsets:
            temp = list()
            try:
                language_synset = db(self.language, "synset")

                if language_synset:
                    language_synset.execute(f"SELECT * FROM {self.language}_synset")
                    results = language_synset.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        synset = Synset(result[0], self.language)
                        temp.append(synset)
                        yield synset
            self._synsets = temp
        return (synset for synset in self._synsets)

    def get_synsets(self, pos: str = 'nvar') -> Generator['Synset', None, Iterable['Synset']]:
        if not self._synsets:
            temp = list()
            try:
                if pos == 'nvar':
                    pos_query = ''
                else:
                    pos_query = f" WHERE id LIKE '{pos}%'"

                language_synset = db(self.language, "synset")

                if language_synset:
                    language_synset.execute(f"SELECT * FROM {self.language}_synset{pos_query}")
                    results = language_synset.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        synset = Synset(result[0], self.language)
                        temp.append(synset)
                        yield synset
            self._synsets = temp
        return (synset for synset in self._synsets)


    @lru_cache(maxsize=2048)
    def get_lemma(self, lemma, pos='*', miscellanea=None) -> Lemma:
        return Lemma(lemma=lemma, pos=pos, language=self.language, miscellanea=miscellanea, id=None)

    @lru_cache(maxsize=2048)
    def get(self, lemma, pos='*', miscellanea=None, mode=None) -> List[Lemma]:
        lquery = pquery = mquery = ''
        if lemma:
            lemma = lemma.replace(' ', '_')
            if "''" in lemma:
                pass
            elif "'" in lemma:
                lemma = lemma.replace("'", "''")
            if mode:
                if mode == 'startswith':
                    lquery = f"lemma LIKE '{lemma}%'"
                elif mode == 'endswith':
                    lquery = f"lemma LIKE '%{lemma}'"
                else:
                    lquery = f"lemma LIKE '%{lemma}%'"
            else:
                lquery = f"lemma='{lemma}'"
        if pos:
            if pos in 'nvar':
                pquery += f"pos='{pos}'"
        if miscellanea:
            mquery = f"miscellanea='{miscellanea}'"
        query = ' AND '.join(filter(None, [lquery, pquery, mquery]))
        if query: query = " WHERE " + query

        _list = []
        if self.language == 'latin':
            try:
                language_morpho = db(self.language, "morpho")
                if language_morpho:
                    language_morpho.execute(f"SELECT lemma, pos, miscellanea, id FROM {self.language}_morpho{query};")
                    results = language_morpho.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        lemma, pos, miscellanea, id = result
                        l = Lemma(lemma=lemma, pos=pos, miscellanea=miscellanea, id=id, language=self.language)
                        _list.append(l)
        else:
            try:
                language_lemma = db(self.language, "lemma")

                if language_lemma:
                    language_lemma.execute(f"SELECT lemma, pos FROM {self.language}_lemma{query};")
                    results = language_lemma.fetchall()
            except OperationalError:
                raise
            else:
                if results:
                    for result in set(results):
                        lem = Lemma(result[0], result[1], miscellanea=None, id=None, language=self.language)
                        if lem is not None:
                            _list.append(lem)
        return _list

    @lru_cache(maxsize=1048)
    def get_raw(self, lemma: str=None, pos: str=None, morpho: str=None, mode=None) -> list:
        try:
            lquery = pquery = mquery = ''
            if lemma:
                lemma = lemma.replace(' ', '_')
                if "''" in lemma:
                    pass
                elif "'" in lemma:
                    lemma = lemma.replace("'", "''")
                if mode:
                    if mode == 'startswith':
                        lquery = f"lemma LIKE '{lemma}%'"
                    elif mode == 'endswith':
                        lquery = f"lemma LIKE '%{lemma}'"
                    else:
                        lquery = f"lemma LIKE '%{lemma}%'"
                else:
                    lquery = f"lemma='{lemma}'"

            if pos:
                if pos in 'nvar':
                    pquery += f"pos='{pos}'"

            if morpho:
                mquery = f"'{morpho}'"

            query = ' AND '.join(filter(None, [lquery, pquery, mquery]))
            if query: query = "WHERE " + query

            language_morpho = db(self.language, "morpho")
            if language_morpho:
                language_morpho.execute(f"SELECT lemma, pos, miscellanea FROM {self.language}_morpho {query}")
                results = language_morpho.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if results:
                yield from (result for result in results)

    @property
    def semfields(self) -> Generator['Semfield', None, Iterable['Semfield']]:
        if not self._semfields:
            self._semfields = list()
            try:
                common_semfield_hierarchy = db("common", "semfield_hierarchy")

                if common_semfield_hierarchy:
                    common_semfield_hierarchy.execute("SELECT code, english FROM semfield_hierarchy")
                    results = common_semfield_hierarchy.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        semfield = Semfield(code=result[0], english=result[1], language=self.language)
                        self._semfields.append(semfield)
                        yield semfield
        return (semfield for semfield in self._semfields)

    def get_semfield_by_code(self, code: str) -> List['Semfield']:
        try:
            common_semfield_hierarchy = db("common", "semfield_hierarchy")

            if common_semfield_hierarchy:
                common_semfield_hierarchy.execute(f"SELECT english FROM semfield_hierarchy WHERE code='{code}'")
                results = common_semfield_hierarchy.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if results:
                _semfield = [Semfield(result[0], code=code, language=self.language) for result in results]
            else:
                _semfield = None
            return _semfield

    def get_semfield_by_english(self, english: str) -> List['Semfield']:
        try:
            english = english.replace(' ', '_')
            common_semfield_hierarchy = db("common", "semfield_hierarchy")

            if common_semfield_hierarchy:
                common_semfield_hierarchy.execute(f"SELECT code FROM semfield_hierarchy WHERE english='{english}'")
                results = common_semfield_hierarchy.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if results:
                _semfield = [Semfield(english=english, code=result[0], language=self.language) for result in results]
            else:
                _semfield = None
            return _semfield

    def get_semfield(self, code: str, english: str) -> Semfield:
        return Semfield(code=code, english=english, language=self.language)

    @property
    def lemmas(self) -> Generator[object, None, Iterable[object]]:
        if self._lemmas is None:
            self._lemmas = list()
            try:
                language_morpho = db(self.language, "morpho")

                if language_morpho:
                    language_morpho.execute(f"SELECT lemma, pos, miscellanea, id FROM {self.language}_morpho")
                    results = language_morpho.fetchall()
                else:
                    language_index = db(self.language, "index")

                    if language_index:
                        language_index.execute(f"SELECT * FROM {self.language}_index")
                        results = language_index.fetchall()
                    else:
                        results = None
            except OperationalError:
                raise
            else:
                if results:
                    if language_morpho:
                        for result in results:
                            lemma, pos, miscellanea, id = result
                            lemma = Lemma(lemma=lemma, pos=pos, miscellanea=miscellanea, id=id, language=self.language)
                            self._lemmas.append(lemma)
                            yield lemma
                    else:
                        pos = ['*', 'n', 'v', 'a', 'r']
                        for result in results:
                            for i in range(1, 5):
                                if result[i]:
                                    lemma = Lemma(result[0], pos[i], None, None, self.language)
                                    self._lemmas.append(lemma)
                                    yield lemma

        else:
            yield from (lemma for lemma in self._lemmas)

    def __iter__(self):
        yield from self.lemmas

    def __getitem__(self, key: Tuple[str, str]):
        return self.get_lemma(*key)

    @property
    def relations(self) -> Generator['Relation', None, Iterable['Relation']]:
        if not self._relations:
            self._relations = list()
            try:
                common_relation = db("common", "relation")
                if common_relation:
                    common_relation.execute("SELECT * FROM common_relation")
                    results = common_relation.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        self._relations.append(Relation(*result, language='common'))
            try:
                language_relation = db(self.language, "relation")
                if language_relation:
                    language_relation.execute(f"SELECT * FROM {self.language}_relation")
                    results = language_relation.fetchall()
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        self._relations.append(Relation(*result, language=self.language))
        yield from self._relations

    def get_relations(self, *, source: Synset=None, target: Synset=None, w_source: Lemma=None, w_target: Lemma=None, type=None, lexical=False) -> Generator['Relation', None, Iterable['Relation']]:
        temp = list()
        W_SOURCE = W_TARGET = SOURCE = TARGET = TYPE = SYNSETS = ''
        if lexical or type in ['\\', '/', '+c' '-c']:
            if w_source:
                W_SOURCE = f"w_source='{w_source.lemma}'"
            if w_target:
                W_TARGET = f"w_target='{w_target.lemma}'"
        elif not lexical and type not in ['\\', '/', '+c' '-c']:
            if w_source and not source:
                SYNSETS = [synset.id for synset in w_source.synsets]
                SOURCE = f"id_source IN ({','.join(['?' for synset in w_source.synsets])})"
            if w_target and not target:
                SYNSETS = [synset.id for synset in w_target.synsets]
                SOURCE = f"id_target IN ({','.join(['?' for synset in w_target.synsets])})"
        if source:
            SOURCE = f"id_source='{source.id}'"
        if target:
            TARGET = f"id_target='{target.id}'"
        if type:
            TYPE = f"type='{type}'"
        QR = ' AND '.join(filter(lambda x: x != '', [SOURCE, TARGET, W_SOURCE, W_TARGET, TYPE]))

        if not lexical:
            try:
                common_relation = db("common", "relation")
                if common_relation:
                    common_relation.execute("SELECT * FROM common_relation WHERE " + QR, SYNSETS)
                    results = common_relation.fetchall()
                else:
                    results = None
            except OperationalError:
                raise
            else:
                if results:
                    for result in results:
                        temp.append(Relation(*result, language='common'))
        try:
            language_relation = db(self.language, "relation")

            if language_relation:
                language_relation.execute(f"SELECT * FROM {self.language}_relation WHERE " + QR, SYNSETS)
                results = language_relation.fetchall()
            else:
                results = None
        except OperationalError:
            raise
        else:
            if results:
                for result in results:
                    type, id_source, id_target, w_source, w_target, status = result
                    relation = Relation(type=type, id_source=id_source, id_target=id_target, w_source=w_source, w_target=w_target, language=self.language)
                    temp.append(relation)
        yield from temp

    def __repr__(self):
        return f"WordNet('{self.language}')"

    @lru_cache()
    def max_depth_for(self, pos: str):
        """
        Compute the max depth for the given part of speech.  This is
        used by the lch similarity metric.
        """
        depth = 0
        for ii in self.get_synsets(pos):
            depth = max(depth, ii.max_depth())
        return depth

# Helper functions
def breadth_first(tree, children=iter, maxdepth=-1):
    """Traverse the nodes of a tree in breadth-first order.
    (No need to check for cycles.)
    The first argument should be the tree root;
    children should be a function taking as argument a tree node
    and returning an iterator of the node's children.
    """
    queue = deque([(tree, 0)])

    while queue:
        node, depth = queue.popleft()
        yield node

        if depth != maxdepth:
            try:
                queue.extend((c, depth + 1) for c in children(node))
            except TypeError:
                pass
