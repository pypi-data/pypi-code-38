# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science.
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import logging
from typing import Iterable, List, Optional, Set

import pandas as pd
import sqlalchemy
import whoosh.index
from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import make_transient
from whoosh.qparser import FuzzyTermPlugin, QueryParser

from . import PROTON_INCHI, WATER_INCHI
from .models import Compound, CompoundIdentifier, Registry


__all__ = ("CompoundCache",)


logger = logging.getLogger(__name__)
Session = sessionmaker()


class CompoundCache:
    """
    Implement a compound cache for look ups.

    CompoundCache is a singleton that handles caching of Compound objects for
    the component-contribution package.  The Compounds are retrieved by their
    ID (e.g., KEGG COMPOUND ID, ChEBI Id or HMDB in most cases) or InChI Key.
    The first time a Compound is requested, it is obtained from the relevant
    database and a Compound object is created. Any further
    request for the same Compound ID will draw the object from the cache. When
    the method dump() is called, all cached data is written to a file that will
    be loaded in future python sessions.

    """

    def __init__(
        self,
        engine: sqlalchemy.engine.base.Engine,
        search_index: Optional[whoosh.index.Index] = None,
    ):
        """Initialize an in memory cache for compounds."""
        self.compound_dict = {}
        self.engine = engine
        self.session = Session(bind=self.engine)
        self.idx = search_index
        self._proton = None
        self._water = None

    @property
    def proton(self):
        if self._proton is None:
            self._proton = self.get_compound_by_inchi(PROTON_INCHI)
        return self._proton

    @property
    def water(self):
        if self._water is None:
            self._water = self.get_compound_by_inchi(WATER_INCHI)
        return self._water

    def all_compound_accessions(self, ascending: bool = True) -> List[str]:
        return sorted(
            (
                row.accession
                for row in self.session.query(
                    CompoundIdentifier.accession
                ).distinct()
            ),
            reverse=not ascending,
        )

    def accession_exists(self, accession: str) -> bool:
        return self.session.query(
            exists().where(CompoundIdentifier.accession == accession)
        ).scalar()

    def get_compound_by_internal_id(self, compound_id: int) -> Compound:
        """Find a compound in the cache based on the internal ID."""
        return (
            self.session.query(Compound).filter_by(id=compound_id).one_or_none()
        )

    def get_compound_by_inchi(self, inchi: str) -> Optional[Compound]:
        """Return a compound by exact match of the InChI."""
        hits = self.session.query(Compound).filter_by(inchi=inchi).all()
        if len(hits) == 0:
            return None
        if len(hits) == 1:
            return hits[0]
        else:
            compound = hits[0]
            # We don't want to persist the following changes to identifiers
            # to the database. Thus we detach this object from the session.
            make_transient(compound)
            for cmpd in hits[1:]:
                compound.identifiers.extend(cmpd.identifiers)
            return compound

    def search_compound_by_inchi_key(self, inchi_key: str) -> List[Compound]:
        """
        Return all compounds matching the (partial) InChI Key.

        Certain parts at the end of an InChI Key may be omitted in order to
        omit specific InChI layers of information and retrieve all generally
        matching compounds.

        """
        query = self.session.query(Compound)
        if len(inchi_key) < 27:
            return query.filter(Compound.inchi_key.like(f"{inchi_key}%")).all()
        else:
            return query.filter_by(inchi_key=inchi_key).all()

    def get_compound(self, compound_id: str) -> Compound:
        try:
            namespace, accession = compound_id.split(":", 1)
        except ValueError:
            namespace, accession = None, compound_id
        else:
            # Special case for ChEBI identifiers.
            if namespace == "CHEBI":
                namespace = "chebi"
                accession = compound_id
            else:
                namespace = namespace.lower()

        return self.get_compound_from_registry(namespace, accession)

    def get_compound_from_registry(
        self, namespace: str, accession: str
    ) -> Compound:

        if (namespace, accession) in self.compound_dict:
            logging.debug(f"Cache hit for {accession} in {namespace} in RAM")
            return self.compound_dict[(namespace, accession)]

        query = self.session.query(Compound)
        if namespace == "inchi_key":
            # try to find this compound by assuming the input is an InChIKey
            logging.debug(f"Looking for {accession} as InChIKey")
            query = query.filter_by(inchi_key=accession)
        else:
            query = query.join(CompoundIdentifier).filter(
                CompoundIdentifier.accession == accession
            )
            if namespace is None:
                # if the namespace is not given, use the accession alone to
                # find the compound
                logging.debug(f"Looking for {accession} in all namespaces")
            else:
                # otherwise, use the specific namespace and accession to
                # locate the compound.
                logging.debug(f"Looking for {accession} in {namespace}")
                query = query.join(Registry).filter(
                    Registry.namespace == namespace
                )

        compound = query.one_or_none()

        if compound is None:
            logging.debug(f"Cache miss")
            return None
        else:
            logging.debug(f"Cache hit")
            self.compound_dict[(namespace, accession)] = compound
            return compound

    def cache_registry_in_ram(self, namespace: str) -> None:
        if namespace == "mnx":
            query = self.session.query(Compound, Compound.mnx_id).filter(
                Compound.mnx_id.isnot(None)
            )
        elif namespace == "inchi_key":
            query = self.session.query(Compound, Compound.inchi_key).filter(
                Compound.inchi_key.isnot(None)
            )
        elif namespace is None:
            raise ValueError("namespace cannot be None")
        else:
            registry = (
                self.session.query(Registry)
                .filter(Registry.namespace == namespace)
                .one_or_none()
            )
            if registry is None:
                raise ValueError(f"namespace '{namespace}' was not found")

            query = (
                self.session.query(Compound, CompoundIdentifier.accession)
                .join(CompoundIdentifier)
                .filter(CompoundIdentifier.compound_id == Compound.id)
                .filter(CompoundIdentifier.registry_id == registry.id)
            )
            if namespace == "kegg":
                query = query.filter(CompoundIdentifier.accession.like("C%"))
            query = query.group_by(Compound.id)

        for compound, accession in query:
            if (namespace, accession) not in self.compound_dict:
                self.compound_dict[(namespace, accession)] = compound

    @staticmethod
    def get_element_data_frame(compounds: Iterable[Compound]) -> pd.DataFrame:
        """
        Tabulate the elemental composition of the given compounds.

        Parameters
        ----------
        compounds : iterable
            A collection of compounds.

        Returns
        -------
        pandas.DataFrame
            A data frame where the columns are the compounds and the
            indexes are atomic elements.

        """
        atom_bags = {
            compound: compound.atom_bag or {} for compound in compounds
        }

        # create the elemental matrix, where each row is a compound and each
        # column is an element (or e-)
        return pd.DataFrame.from_dict(
            atom_bags, orient="columns", dtype=int
        ).fillna(0)

    def get_compound_names(self, compound: Compound) -> Set[str]:
        """Return the most common name for this compound."""
        query = (
            self.session.query(CompoundIdentifier)
            .join(Registry)
            .filter(CompoundIdentifier.compound_id == compound.id)
            .filter(CompoundIdentifier.registry_id == Registry.id)
            .filter(Registry.name == "Synonyms")
        )

        names = set()
        for identifier in query:
            names.update(identifier.accession.split("|"))
        return names

    def get_compound_first_name(self, compound: Compound) -> str:
        """Return the most common name for this compound."""
        identifier = (
            self.session.query(CompoundIdentifier)
            .join(Registry)
            .filter(CompoundIdentifier.compound_id == compound.id)
            .filter(CompoundIdentifier.registry_id == Registry.id)
            .filter(Registry.name == "Synonyms")
        ).first()
        return identifier.accession.split("|")[0]

    def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> List[Compound]:
        """
        Parse the given query and return matching compounds.

        Parameters
        ----------
        query : str
            The desired search term(s).
        page : int
            The desired page (default 1st).
        page_size : int
            The number of compounds per page.

        Returns
        -------
        list
            A list of compounds from the specified search result page.

        """
        if self.idx is None:
            raise RuntimeError(
                "No search index present. Please initialize a "
                "Whoosh search index first."
            )
        parser = QueryParser("name", schema=self.idx.schema)
        parser.add_plugin(FuzzyTermPlugin())
        parsed = parser.parse(query)
        with self.idx.searcher() as searcher:
            search = [
                r["compound_id"]
                for r in searcher.search_page(parsed, page, pagelen=page_size)
            ]
            # TODO (Moritz Beber): Order by search relevance score.
            results = (
                self.session.query(Compound)
                .filter(Compound.id.in_(search))
                .all()
            )
        return results
