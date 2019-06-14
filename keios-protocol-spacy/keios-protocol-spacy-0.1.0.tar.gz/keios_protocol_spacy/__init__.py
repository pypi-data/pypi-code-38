from enum import Enum
from typing import List
from dataclasses import dataclass
import numpy as np
import flatbuffers
from keios_protocol_common import FlatbufferObject
from keios_protocol_spacy.flatbuffers import DEPSpacyResponse as DEPSpacyResponseClass
from keios_protocol_spacy.flatbuffers import NERSpacyResponse as NERSpacyResponseClass
from keios_protocol_spacy.flatbuffers import SpacyRequest as SpacyRequestClass
from keios_protocol_spacy.flatbuffers import SpacyResponse as SpacyResponseClass
from keios_protocol_spacy.flatbuffers import Type as TypeClass

@dataclass
class DEPSpacyResponseData:
    lang: str
    relation: str
    source: str
    source_pos: str
    source_index: int
    source_tag: str
    source_base: str
    target: str
    target_pos: str
    target_index: int
    target_tag: str
    target_base: str

class DEPSpacyResponseEntity(FlatbufferObject):
    def __init__(self, builder):
        super().__init__(DEPSpacyResponseData, DEPSpacyResponseClass, builder)

    def dataclass_to_flatbuffer(self, dataclass):
        str_attr_dict = {}
        for str_attr in [
            'lang',
            'relation',
            'source',
            'source_pos',
            'source_tag',
            'source_base',
            'target',
            'target_pos',
            'target_tag',
            'target_base'
        ]:
            str_attr_dict[str_attr] = self.build_string(getattr(dataclass, str_attr))
        self.start()
        # set string attributes
        self['Lang']        = str_attr_dict['lang']
        self['Relation']    = str_attr_dict['relation']
        self['Source']      = str_attr_dict['source']
        self['SourcePos']   = str_attr_dict['source_pos']
        self['SourceTag']   = str_attr_dict['source_tag']
        self['SourceBase']  = str_attr_dict['source_base']
        self['Target']      = str_attr_dict['target']
        self['TargetPos']   = str_attr_dict['target_pos']
        self['TargetTag']   = str_attr_dict['target_tag']
        self['TargetBase']  = str_attr_dict['target_base']
        # set other attributes
        self['SourceIndex'] = dataclass.source_index
        self['TargetIndex'] = dataclass.target_index
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        return DEPSpacyResponseData(
            lang            = self['Lang'].decode("utf-8"),
            relation        = self['Relation'].decode("utf-8"),
            source          = self['Source'].decode("utf-8"),
            source_pos      = self['SourcePos'].decode("utf-8"),
            source_index    = self['SourceIndex'],
            source_tag      = self['SourceTag'].decode("utf-8"),
            source_base     = self['SourceBase'].decode("utf-8"),
            target          = self['Target'].decode("utf-8"),
            target_pos      = self['TargetPos'].decode("utf-8"),
            target_index    = self['TargetIndex'],
            target_tag      = self['TargetTag'].decode("utf-8"),
            target_base     = self['TargetBase'].decode("utf-8")
        )

@dataclass
class NERSpacyResponseData:
    text: str
    start_char: int
    end_char: int
    label: str

class NERSpacyResponseEntity(FlatbufferObject):
    def __init__(self, builder):
        super().__init__(NERSpacyResponseData, NERSpacyResponseClass, builder)

    def dataclass_to_flatbuffer(self, dataclass):
        text = self.build_string(dataclass.text)
        label = self.build_string(dataclass.label)
        self.start()
        # set string attributes
        self['Text']      = text
        self['Label']     = label
        # set other attributes
        self['StartChar'] = dataclass.start_char
        self['EndChar']   = dataclass.end_char
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        return NERSpacyResponseData(
            text        = self['Text'].decode("utf-8"),
            start_char  = self['StartChar'],
            end_char    = self['EndChar'],
            label       = self['Label'].decode("utf-8")
        )

@dataclass
class SpacyResponseData:
    ner: List[NERSpacyResponseData]
    dep: List[DEPSpacyResponseData]

class SpacyResponseEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(SpacyResponseData, SpacyResponseClass)
    
    def dataclass_to_flatbuffer(self, dataclass):
        dep_vector = self.build_vector('Dep', dataclass.dep, DEPSpacyResponseEntity)
        ner_vector = self.build_vector('Ner', dataclass.ner, NERSpacyResponseEntity)
        self.start()
        self['Dep'] = dep_vector
        self['Ner'] = ner_vector
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        ner = NERSpacyResponseEntity(self.builder)
        dep = DEPSpacyResponseEntity(self.builder)
        return SpacyResponseData(
            ner = [ner.build(g) for n in self['Ner']],
            dep = [dep.build(g) for d in self['Dep']]
        )

class TypeData(Enum):
    DEP = 0
    NER = 1

@dataclass
class SpacyRequestData:
    text: str
    type: List[TypeData]

class SpacyRequestEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(SpacyRequestData, SpacyRequestClass)

    def dataclass_to_flatbuffer(self, dataclass):
        dep_vector = self.build_vector('Dep', dataclass.dep, DEPSpacyResponseEntity)
        ner_vector = self.build_vector('Ner', dataclass.dep, NERSpacyResponseEntity)
        self.start()
        self['Dep'] = dep_vector
        self['Ner'] = ner_vector
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        return SpacyRequestData(
            text = self['Text'].decode("utf-8"),
            type = [TypeData(n) for n in self['Type']]
        )