"""Handles Snomed-CT conversion.

This module provides methods to extract, transform and load relationships
defined by the SNOMED CT dataset.

The download files for SNOMED CT are provided at https://www.nlm.nih.gov/healthit/snomedct/.
"""
import petl as etl
import json
import os

from termlink.commands import SubCommand
from termlink.models import Coding, Relationship, RelationshipSchema
from termlink.services import RelationshipService
from os import listdir
from dataclasses import replace
from urllib.parse import urlparse

_STATED_RELATIONSHIP_FILE_FIELDS = ["id", "effectiveTime", "active", "moduleId", "sourceId", "destinationId",
                                    "relationshipGroup", "typeId", "characteristicTypeId", "modifierId"]
_DESCRIPTION_FILE_FIELDS = ["id", "effectiveTime", "active", "moduleId", "conceptId", "languageCode", "typeId",
                            "term", "caseSignificanceId"]
_IS_A_TYPE_ID = "116680003"
_FULLY_SPECIFIED_NAME_TYPE_ID = "900000000000003001"
_FIRST_LETTER_CAPITAL_CASE_ID = "900000000000020002"


def _to_json(rec):
    """
    Convert record in table to Relationship as a JSON object

    Record is expected to have the following fields: [ source.CODE, source.STR, target.CODE, target.STR]

    Args:
        rec: A table record

    Returns:
        A new record containing a single field, which is the JSON object
    """

    source = Coding(
        system="http://snomed.info/sct",
        code=rec['sourceId'],
        display=rec['source.term'],
        version=rec['effectiveTime'] if rec['versioned'] else None
    )

    target = Coding(
        system="http://snomed.info/sct",
        code=rec['destinationId'],
        display=rec['target.term'],
        version=rec['effectiveTime'] if rec['versioned'] else None
    )

    relationship = Relationship('subsumes', source, target)

    schema = RelationshipSchema()
    return [json.dumps(schema.dump(relationship))]


class Command(SubCommand):
    """
    A command executor for Snomed-CT operations
    """

    @staticmethod
    def execute(args):
        """
        Prints a JSON array of `Relationship` objects to stdout

        Args:
            args: `argparse` parsed arguments
        """
        uri = urlparse(args.uri)
        service = Service(uri, args.versioned, args.include_inactive)
        table = service.get_relationships()
        if table:
            etl.io.totext(table, encoding='utf8', template='{relationship}\n')



class Service(RelationshipService):
    """Converts the SNOMED CT database"""

    def __init__(self, uri, versioned=False, include_inactive=False):
        """
        Bootstraps a service

        Args:
            uri: URI to root location of .rrf files
            versioned: Flag to indicate whether to include version mapping
            include_inactive: Flag to indicate whether to transform inactive relationship or not. Default is active only.
        """

        if uri.scheme != 'file':
            raise ValueError("'uri.scheme' %s not supported" % uri.scheme)

        self.uri = uri
        self.versioned = versioned
        self.include_inactive = include_inactive

    def get_file_name(self, files, file_type):
        for file in files:
            if file_type in file:
                return os.path.join(self.uri.path, file)
        raise ValueError("Unable to find \"" + file_type + "\" file in the directory files (" + str(files) + ")!")

    def get_relationships(self):
        """
        Parses a list of `Relationship` objects.
        """
        files = listdir(self.uri.path)

        path = self.get_file_name(files, "StatedRelationship")
        relationship = etl \
            .fromcsv(path, delimiter='\t') \
            .setheader(_STATED_RELATIONSHIP_FILE_FIELDS) \
            .select(lambda rec: rec['typeId'] == _IS_A_TYPE_ID)

        # Include inactive if requested
        if not self.include_inactive:
            relationship = relationship \
                .select(lambda rec: rec['active'] == '1')

        relationship = relationship \
            .groupselectlast(['sourceId', 'destinationId', 'typeId']) \
            .cut('effectiveTime', 'sourceId', 'destinationId')

        if relationship.nrows() == 0:
            return None

        path = self.get_file_name(files, "Description")
        description = etl \
            .fromcsv(path, delimiter='\t') \
            .setheader(_DESCRIPTION_FILE_FIELDS) \
            .select(lambda rec: rec['typeId'] == _FULLY_SPECIFIED_NAME_TYPE_ID) \
            .select(lambda rec: rec['caseSignificanceId'] == _FIRST_LETTER_CAPITAL_CASE_ID) \
            .sort(['conceptId', 'effectiveTime'], reverse=True) \
            .cut('conceptId', 'term')

        relationship_with_description = relationship \
            .lookupjoin(description, lkey="sourceId", rkey="conceptId", rprefix="source.") \
            .lookupjoin(description, lkey="destinationId", rkey="conceptId", rprefix="target.") \
            .addfield('versioned', self.versioned) \
            .rowmap(_to_json, ['effectiveTime', 'sourceId', 'destinationId', 'source.term', 'target.term',
                               'versioned']) \
            .setheader(['relationship'])

        return relationship_with_description
