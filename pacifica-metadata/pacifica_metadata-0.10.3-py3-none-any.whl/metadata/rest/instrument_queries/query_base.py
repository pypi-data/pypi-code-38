#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata projectinfo base class."""
from pacifica.metadata.orm.instrument_group import InstrumentGroup
from pacifica.metadata.orm.groups import Groups


class QueryBase(object):
    """Retrieves a set of instruments for a given keyword set."""

    @staticmethod
    def format_instrument_block(instrument_entry):
        """Construct a dictionary from a given instrument instance in the metadata stack."""
        _ie = instrument_entry
        # pylint: disable=no-member
        g_names = Groups.select(
            Groups.name
        ).join(
            InstrumentGroup
        ).where(
            InstrumentGroup.instrument == _ie.id
        )
        # pylint: enable=no-member
        category = g_names[0].name if g_names else 'Miscellaneous'
        name = _ie.name
        display_name = u'[{0} / ID:{1}] {2}'.format(
            category, _ie.id, name
        )
        return {
            'id': _ie.id,
            'category': category,
            'groups': [g.name for g in g_names],
            'display_name': display_name,
            'name': name,
            'name_short': _ie.name_short,
            'active': _ie.active
        }

    @staticmethod
    def instrument_help_block_message():
        """Assemble a block of relevant help text to be returned with an invalid request."""
        message = 'You must supply either a instrument id (like "/instrumentinfo/<instrument_id>")'
        message += ' or search for one using the form "/instrumentinfo/search/<search_term_1>+<search_term_2>"'
        return message
