# -*- coding: utf-8 -*-
"""
Validates cadaster parcel in Flanders
"""

import re

import colander
from colander import null


class CadasterSchemaNode(colander.MappingSchema):

    afdeling = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    sectie = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    perceel = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    capakey = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50)
    )

    @staticmethod
    def preparer(parcel):
        if parcel is None or not parcel:
            return null  # pragma: no cover
        return parcel

    @staticmethod
    def validator(node, parcel):
        capakey = parcel.get('capakey', None)
        match = False
        if capakey:
            match = re.match(
                r"^[0-9]{5}[A-Z]{1}([0-9]{4})\/([0-9]{2})([A-Z\_]{1})([0-9]{3})$",
                capakey
            )
        if not capakey or not match:
            raise colander.Invalid(
                    node,
                    'Ongeldige capakey'
            )
