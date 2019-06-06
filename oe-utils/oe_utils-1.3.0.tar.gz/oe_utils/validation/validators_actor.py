# -*- coding: utf-8 -*-
'''
This module allows for the validation of actor data like national ID number and telephone.
'''

import colander
import re


def is_number(s):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


class RRNSchemaNode(colander.SchemaNode):
    title = 'rrn'
    schema_type = colander.String

    @staticmethod
    def validator(node, rrn):
        '''
        Colander validator that checks whether a given value is a valid
        Belgian national ID number .
        :raises colander.Invalid: If the value is no valid Belgian national ID number.
        '''

        def _valid(_rrn):
            x = 97 - (int(_rrn[:-2]) - (int(_rrn[:-2]) // 97) * 97)
            return int(_rrn[-2:]) == x

        if len(rrn) != 11:
            raise colander.Invalid(
                node,
                'Een rijksregisternummer moet 11 cijfers lang zijn.'
            )
        elif not _valid(rrn):
            valid_rrn = False
            if rrn[:1] == '0' or rrn[:1] == '1':
                rrn = '2' + rrn
                valid_rrn = _valid(rrn)
            if not valid_rrn:
                raise colander.Invalid(
                    node,
                    'Dit is geen correct rijksregisternummer.'
                )


class KBOSchemaNode(colander.SchemaNode):
    title = 'kbo'
    schema_type = colander.String

    @staticmethod
    def preparer(value):
        '''
        Edit a value to a value that can be validated as a
        kbo number.
        '''
        if value is None or value == colander.null:
            return colander.null
        return value.strip().replace('.', '')

    @staticmethod
    def validator(node, value):
        '''
        Colander validator that checks whether a given value is a valid
        is company number.
        For our purposes , we expect a firm number that
        is composed of nine or ten characters like 2028445291.
        Sometimes a company number is formatted with separation marks like 0.400.378.485.
        Therefore, there is also a : Func: ` actoren.validators.kbo_preparer` which transforms such input.
        :raises colander.Invalid: if the value is valid Belgian company number.
        '''

        if not re.match(r'^[0-9]{9,10}$', value):
            raise colander.Invalid(
                node,
                'Dit is geen correct ondernemingsnummer.'
            )


class TelefoonSchemaNode(colander.MappingSchema):
    landcode = colander.SchemaNode(
        colander.String(),
        missing="+32"
    )
    nummer = colander.SchemaNode(
        colander.String(),
        missing=""
    )

    @staticmethod
    def preparer(telefoon):
        '''
        Edit a phone value to a value that can be validated as a
        phone number.
        This takes the incoming value and :
            Removes all whitespace ( space, tab , newline , ... ) characters
            Removes the following characters: " / - . "
            If no + is present at frond, add the country code
            In short: just add a + at the beginning of the country code.
        '''
        if telefoon is None or telefoon == colander.null:
            return colander.null
        if 'landcode' in telefoon and telefoon.get('landcode') is not None:
            landcode = telefoon.get('landcode')
            value = re.sub(r'\s+', '', landcode).replace('.', '').replace('/', '').replace(',', '').replace('-', ''). \
                lstrip('0')
            telefoon['landcode'] = '+' + value if value[0] != '+' else value
        if 'nummer' in telefoon and telefoon.get('nummer') is not None:
            nummer = telefoon.get('nummer')
            value = re.sub(r'\s+', '', nummer).replace('.', '').replace('/', '').replace(',', '').replace('-', ''). \
                lstrip('0')
            telefoon['nummer'] = value
        return telefoon

    @staticmethod
    def validator(node, telefoon):
        ''' A valid international phone number looks like this: + .
        It is up to 15 digits long . The country code consists of 1 to 4 digits.
        The actual number may even 15 - cells ( country code) figures cover . We're going to keep the phone numbers including a + to indicate the international call prefix.
        A valid number always begins with a + . The shortest valid number that we want to keep is: +11 ( 3 characters). The longest : +123123456789123 (16 characters).
        Additional validation (after preparation ) : If a number starts with +32 (this is a Belgian number) , it must then follow eight or nine digits . The first decimal after +32 may not be 0 .
        '''
        if telefoon.get('nummer', '') != "":
            msg = "Invalid phone number"
            landcode = telefoon.get('landcode', '')
            nummer = telefoon.get('nummer', '')
            if landcode[0] != '+' or len(landcode[1:]) > 4 or not is_number(landcode[1:]):
                raise colander.Invalid(node,
                                       msg + ': Een geldige landcode begint met een + gevolgd door maximaal 4 cijfers')
            if landcode[0] != '+' or len(landcode[1:]) + len(nummer) > 15 or not is_number(nummer):
                raise colander.Invalid(node,
                                       msg + ': Een geldige nummer begint met een + gevolgd door maximaal 15 cijfers')
            # validatie van Belgische telefoonnummers
            if landcode == '+32':
                if len(nummer) not in [8, 9]:
                    raise colander.Invalid(node, msg + ': Na +32 moeten er 8 of 9 cijfers volgen')
