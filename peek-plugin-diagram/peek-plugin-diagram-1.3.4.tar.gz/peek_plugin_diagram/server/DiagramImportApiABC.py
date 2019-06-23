from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred


class DiagramImportApiABC(metaclass=ABCMeta):
    @abstractmethod
    def importDisps(self, modelSetKey: str, coordSetKey: str, importGroupHash: str,
                    dispsEncodedPayload: bytes) -> Deferred:
        """ Import Disps

        Add or replace display items in a model

        :param modelSetKey:  The name of the model set to import the disps into
        :param coordSetKey:  The name of the cooridinate set to import the disps into
        :param importGroupHash:  The unique hash of the input group to import into
        :param dispsEncodedPayload: An array of disps to import, wrapped in a serialised
                    payload.


        Wrap the disps list with ::

                dispsEncodedPayload = Payload(tuples=disps).toEncodedPayload()


        :return: A deferred that fires when the disps are loaded and queued for compile

        """

    @abstractmethod
    def importLookups(self, modelSetKey: str, coordSetKey: str,
                      lookupTupleType: str, lookupTuples: List,
                      deleteOthers: bool = True,
                      updateExisting: bool = True) -> Deferred:
        """ Import Lookups

        Add or replace diplay lookups in a model

        :param modelSetKey:  The name of the model set to import the lookups into
        :param coordSetKey:  The name of the coord set to import the lookups into
        :param lookupTupleType:  The type of lookups being imported
        :param lookupTuples: An array of the lookups
        :param deleteOthers: Delete existing lookups that are not present in lookupTuples
        :param updateExisting: If a lookup already exists, update it.
                This is matched by the "importHash"

        :return: A deferred that fires when the lookups are imported

        """

    @abstractmethod
    def getLookups(self, modelSetKey: str, coordSetKey: str,
                   lookupTupleType: str) -> Deferred:
        """ Get Lookups

        Use this method to retrieve lookups that have been previously imported.

        :param modelSetKey:  The name of the model set for the lookups
        :param coordSetKey:  The name of the coord set for the lookups
        :param lookupTupleType:  The type of lookups to return

        :return: A deferred that fires with a list of lookup tuples. These tuples
                are the same type used during the import.

        """
