# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Constants relevant to Universal Dependencies.

For tag to feature conversion use conversions available at
see http://universaldependencies.org/docs/tagset-conversion/index.html
"""

from enum import Enum
from typing import Mapping, List


class UPos(Enum):
    """
    Universal POS tags.
    See http://universaldependencies.org/u/pos/all.html
    """
    # === Open class ===
    ADJ = 1
    """ adjective """
    ADV = 2
    """ adverb """
    INTJ = 3
    """ interjection """
    NOUN = 4
    """ noun """
    PROPN = 5
    """ proper noun """
    VERB = 6
    """ verb """

    # === Closed class ===
    ADP = 7
    """ adposition (preposition or postposition)"""
    AUX = 8
    """ auxiliary """
    CCONJ = 9
    """ coordianting conjunction """
    DET = 10
    """ determiner """
    NUM = 11
    """ numeral """
    PRON = 12
    """ pronoun """
    PART = 13
    """ particle """
    SCONJ = 14
    """ subordinating conjunction """

    PUNCT = 15
    """ punctuation """
    SYM = 16
    """ symbol """
    X = 17
    """ other"""

    @staticmethod
    def fromStr(posStr: str) -> 'UPos':
        """
        Conversion from string with X as a fallback for unknown values

        :param posStr: PoS as a string
        :return: corresponding UPos member or UPos.X
        """
        return getattr(UPos, posStr, UPos.X)

    def toStr(self) -> str:
        """
        Conversion from the enum value to the string value used by the API.
        """
        return self.name


UFeats = Mapping[str, List[str]]
""" TYpe of universal features (generally a multimap from feature names to potentially multiple feature valeus) """


class UDep(Enum):
    """ Universal syntactic dependencies V2 and V1. See http://universaldependencies.org/u/dep/all.html"""

    # Nominals - Core
    NSUBJ = 1
    """ nominal subject """
    OBJ = 2
    """ object (V2) """
    IOBJ = 3
    """ indirect object """

    # Nominals - Non-core dependents
    OBL = 4
    """ oblique nominal (V2) """
    VOCATIVE = 5
    """ vocative """
    EXPL = 6
    """ expletive """
    DISLOCATED = 7
    """ dislocated elements """

    # Nominals - Nominal dependents
    NMOD = 8
    """ nominal modifier """
    APPOS = 9
    """ appositional modifier """
    NUMMOD = 10
    """ numeric modifier """

    # Clauses - Core
    CSUBJ = 11
    """ clausal subject """
    CCOMP = 12
    """ clausal complement """
    XCOMP = 13
    """ open clausal complement """

    # Clauses - Non-core dependents
    ADVCL = 14
    """ adverbial clause modifier """

    # Clauses - Nominal dependent
    ACL = 15
    """ clausal modifier of noun (adjectival clause) """

    # Modifier words - Non-core dependents
    ADVMOD = 16
    """ adverbial modifier """
    DISCOURSE = 17
    """ discourse element """

    # Modifier words - Nominal dependent
    AMOD = 18
    """ adjectival modifier """

    # Function Words - Non-core dependents
    AUX = 19
    """ auxiliary """
    COP = 20
    """  """
    MARK = 21
    """  """

    # Function Words - Nominal dependent
    DET = 22
    """ determiner """
    CLF = 23
    """ classifier (V2) """
    CASE = 24
    """ case marking """

    # Coordination
    CONJ = 25
    """ conjunct """
    CC = 26
    """ coordinating conjunction """

    # MWE
    FIXED = 27
    """ fixed multiword expression (V2) """
    FLAT = 28
    """ flat multiword expressio (V2) """
    COMPOUND = 29
    """ compound """

    # Loose
    LIST = 30
    """ list """
    PARATAXIS = 31
    """ parataxis """

    # Special
    ORPHAN = 32
    """ orphan (V2) """
    GOESWITH = 33
    """ goes with """
    REPARANDUM = 34
    """ overridden disfluency """

    # Other
    PUNCT = 35
    """ punctuation """
    ROOT = 36
    """ root """
    DEP = 37
    """ unspecified dependency """

    # V1
    AUXPASS = 38
    """ passive auxiliary (V1) """
    CSUBJPASS = 39
    """ clausal passive subject (V1) """
    DOBJ = 40
    """ direct object (V1; in V2 as obj) """
    FOREIGN = 41
    """ foreign words (V1) """
    MWE = 42
    """ multi-word expression (V1) """
    NAME = 43
    """ name (V1) """
    NEG = 44
    """ negation modifier (V1) """
    NSUBJPASS = 45
    """ passive nominal subject (V1) """
    REMNANT = 46
    """ remnant in ellipsis (V1) """

    @staticmethod
    def fromStr(depStr: str) -> 'UDep':
        """
        Conversion from string with DEP as a fallback for unknown values

        :param depStr: UDep as a string
        :return: corresponding UDep member or UDep.DEP
        """
        return getattr(UDep, depStr.upper(), UDep.DEP)

    def toStr(self) -> str:
        """
        Conversion from the enum value to the string value used by the API
        (the only difference is that the API uses lower case strings)
        """
        return self.name.lower()
