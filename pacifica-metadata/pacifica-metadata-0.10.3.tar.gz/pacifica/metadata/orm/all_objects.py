#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Core modules.

This loads all model objects and contains global operations
on those objects.
"""
from .citations import Citations
from .contributors import Contributors
from .institution_user import InstitutionUser
from .institutions import Institutions
from .instruments import Instruments
from .instrument_user import InstrumentUser
from .journals import Journals
from .relationships import Relationships
from .data_sources import DataSources
from .keywords import Keywords
from .citation_keyword import CitationKeyword
from .citation_contributor import CitationContributor
from .project_group import ProjectGroup
from .project_instrument import ProjectInstrument
from .users import Users
from .project_user import ProjectUser
from .projects import Projects
from .citation_project import CitationProject
from .files import Files
from .keys import Keys
from .values import Values
from .transsip import TransSIP
from .transsap import TransSAP
from .transactions import Transactions
from .file_key_value import FileKeyValue
from .trans_key_value import TransactionKeyValue
from .groups import Groups
from .user_group import UserGroup
from .instrument_group import InstrumentGroup
from .analytical_tools import AnalyticalTools
from .atool_project import AToolProject
from .atool_transaction import AToolTransaction
from .transaction_user import TransactionUser
from .doi_transaction import DOITransaction
from .citation_transaction import CitationTransaction
from .citation_doi import CitationDOI
from .doi_entries import DOIEntries
from .doi_authors import DOIAuthors
from .doi_author_mapping import DOIAuthorMapping
from .doi_info import DOIInfo
from .instrument_data_source import InstrumentDataSource
from .instrument_key_value import InstrumentKeyValue


ORM_OBJECTS = [
    Journals,
    Users,
    Institutions,
    Projects,
    Instruments,
    Citations,
    Contributors,
    Relationships,
    DataSources,
    Keywords,
    Groups,
    AnalyticalTools,
    InstrumentUser,
    InstitutionUser,
    CitationContributor,
    CitationKeyword,
    ProjectInstrument,
    ProjectUser,
    ProjectGroup,
    CitationProject,
    Transactions,
    TransSIP,
    TransSAP,
    Files,
    Keys,
    Values,
    FileKeyValue,
    TransactionKeyValue,
    UserGroup,
    InstrumentGroup,
    AToolProject,
    AToolTransaction,
    TransactionUser,
    DOIEntries,
    DOIAuthors,
    DOITransaction,
    CitationTransaction,
    CitationDOI,
    DOIAuthorMapping,
    DOIInfo,
    InstrumentDataSource,
    InstrumentKeyValue
]
