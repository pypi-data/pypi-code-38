"""FAM parser.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
"""
import os

import yaml

from bin_parser import BinReader


class FamParser(BinReader):
    def __init__(self, input_handle):
        super(FamParser, self).__init__(
            input_handle,
            yaml.safe_load(open(
                os.path.join(os.path.dirname(__file__), 'structure.yml'))),
            yaml.safe_load(open(
                os.path.join(os.path.dirname(__file__), 'types.yml'))),
            prune=True)

        self._parsed = self.parsed
        self.parsed = {
            'family': {
                'relationships': []},
            'metadata': {}}

        # Extract the relationships and put them in the family structure.
        relationships = {}
        for member in self._parsed['members']:
            spouses = member.pop('spouses')
            for spouse in spouses:
                members = sorted([member['id'], spouse.pop('id')])
                spouse['member_ids'] = members
                relationships['{}_{}'.format(*members)] = spouse

        for item in sorted(relationships):
            self.parsed['family']['relationships'].append(relationships[item])

        # Put all family related data in the family structure.
        for item in ['name', 'id_number', 'comments', 'members']:
            self.parsed['family'][item] = self._parsed.pop(item)

        # Annotate the genetic symbols.
        for index, symbol in enumerate(self._parsed['genetic_symbols']):
            symbol['name'] = self.types[
                't_genetic_symbol']['function']['args']['annotation'][index]

        self.parsed['metadata']['genetic_symbols'] = self._parsed.pop(
            'genetic_symbols')

        # Annotate the additional symbols.
        for index, symbol in enumerate(self._parsed['additional_symbols']):
            symbol['name'] = self.types[
                't_additional_symbol']['function']['args']['annotation'][index]

        # Merge the additional and custom symbols.
        self.parsed['metadata']['additional_symbols'] = self._parsed.pop(
            'additional_symbols') + self._parsed.pop('custom_symbols')

        # Put the rest in the metadata structure.
        self.parsed['metadata'].update(self._parsed)
