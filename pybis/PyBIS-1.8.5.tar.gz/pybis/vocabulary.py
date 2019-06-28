from .utils import VERBOSE
from .openbis_object import OpenBisObject 
from .attribute import AttrHolder
from .definitions import openbis_definitions, fetch_option
import json

class Vocabulary(OpenBisObject):

    def __init__(self, openbis_obj, data=None, terms=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Vocabulary')

        if data is not None:
            self._set_data(data)
            self.__dict__['terms'] = data['terms']

        if terms is None:
            self.__dict__['terms'] = []
        else:
            self.__dict__['terms'] = terms

        if self.is_new:
            allowed_attrs = openbis_definitions(self.entity)['attrs_new']
            for key in kwargs:
                if key not in allowed_attrs:
                    raise ValueError(
                        "{} is an unknown Vocabulary attribute. Allowed attributes are: {}".format(
                            key, ", ".join(allowed_attrs) 
                        ) 
                    )

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        return [
            'get_terms()',
            'add_term(code, label, description)',
            'save()',
        ]

    def get_terms(self):
        """ Returns the VocabularyTerms of the given Vocabulary.
        """
        return self.openbis.get_terms(vocabulary=self.code)


    def add_term(self, code, label=None, description=None):
        """ Adds a term to this Vocabulary.
        If Vocabulary is already persistent, it is added by adding a new VocabularyTerm object.
        If Vocabulary is new, the term is added to the list of terms
        """
        self.__dict__['terms'].append({
            "code": code,
            "label": label,
            "description": description
        })
        

    def save(self):
        terms = self.__dict__['terms']
        for term in terms:
            term["@type"]= "as.dto.vocabulary.create.VocabularyTermCreation"

        if self.is_new:
            request = self._new_attrs('createVocabularies')
            if terms:
                request['params'][1][0]['terms'] = terms 
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Vocabulary successfully created.")
            data = self.openbis.get_vocabulary(resp[0]['permId'], only_data=True)
            self._set_data(data)
            return self

        else:
            request = self._up_attrs('updateVocabularies')
            request['params'][1][0]['vocabularyId'] = {
                "@type": "as.dto.vocabulary.id.IVocabularyId",
                "vocabularyId" : self.code
            }
            if terms:
                request['params'][1][0]['terms'] = terms 
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Vocabulary successfully updated.")
            data = self.openbis.get_vocabulary(self.permId, only_data=True)
            self._set_data(data)


class VocabularyTerm(OpenBisObject):

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'VocabularyTerm')

        if data is not None:
            self._set_data(data)

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    @property
    def vocabularyCode(self):
        if self.is_new:
            return self.__dict__['a'].vocabularyCode
        else:
            return self.data['permId']['vocabularyCode']

    def __dir__(self):
        return [
            'code',
            'vocabularyCode',
            'label',
            'description',
            'official',
            'ordinal',
            'registrator',
            'registrationDate',
            'modifier',
            'modificationDate',
            'move_to_top()',
            'move_after_term()',
        ]

    def move_to_top(self):
        """ Moves the term on the top of the vocabularyTerm list,
        i.e. the ordinal will change
        """
        self.previousTermId = ""

    def move_after_term(self, term):
        """ Moves the term just after the term given. This will result in an ordinal change.
        """
        self.previousTermId = term

    def _up_attrs(self):
        """ AttributeTerms behave quite differently to all other openBIS entities,
        that's why we need to override this method
        """
        attrs = {}
        for attr in 'label description official'.split():
            attrs[attr] = {
                "value": getattr(self, attr),
                "isModified": True,
                "@type": "as.dto.common.update.FieldUpdateValue"
            }

        if not getattr(self, 'previousTermId') == None:
            # internal attribute previousTermId has been touched:
            # set value to either None (i.e. move it to the top) or
            # set value to PREVIOUS_TERM like this:
            value = self.previousTermId
            if value == "":
                value = None
            else:
                permId = {
                    '@type'         : 'as.dto.vocabulary.id.VocabularyTermPermId',
                    'vocabularyCode': self.vocabularyCode,
                    'code'          : value 
                }
                value = permId

            attrs['previousTermId'] = {
                "isModified": True,
                "@type": "as.dto.common.update.FieldUpdateValue",
                "value": value,
            }

        attrs["vocabularyTermId"] = self.vocabularyTermId()
        attrs["@type"] = "as.dto.vocabulary.update.VocabularyTermUpdate"
        request = {
            "method": "updateVocabularyTerms",
            "params": [
                self.openbis.token,
                [attrs]
            ]
        }
        return request


    def _new_attrs(self):
        attrs = {
            "@type": "as.dto.vocabulary.create.VocabularyTermCreation",
            "vocabularyId": self.vocabularyTermId()
        }
        for attr in 'code label description'.split():
            attrs[attr] = getattr(self, attr)

        request = {
            "method": "createVocabularyTerms",
            "params": [
                self.openbis.token,
                [attrs]
            ]
        }
        return request


    def vocabularyTermId(self):
        """ needed for updating a term.
        """
        if self.is_new:
            return {
                "permId": getattr(self, 'vocabularyCode'),
                "@type": "as.dto.vocabulary.id.VocabularyPermId"
            }
        else:
            permId = self.data['permId']
            permId.pop('@id', None)
            return permId


    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Vocabulary Term successfully created.")
            data = self.openbis.get_term(
                code=resp[0]['code'], 
                vocabularyCode=resp[0]['vocabularyCode'],
                only_data=True
            )
            self._set_data(data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Vocabulary Term successfully updated.")
            data = self.openbis.get_term(
                code=self.code, 
                vocabularyCode=self.vocabularyCode,
                only_data=True
            )
            self._set_data(data)


    def delete(self, reason='no particular reason'):
        self.openbis.delete_openbis_entity(
            entity='VocabularyTerm', objectId=self.data['permId'], reason=reason
        )
        if VERBOSE: print("VocabularyTerm successfully deleted.")
