import logging
import pathlib

from typing import List

import pyparsing as pyp

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
log = logging.getLogger(__name__)


def _get_experience_parser(job_titles: List[str]):
    ''' Use pyparsing to process experience

    Extended Backus-Naur form grammar

    number ::= '1.'
    exp_number ::= ('one'|'two'|'three'|...)
    time_period ::= ('years?' | 'month?')
    of ::= 'of'
    exp_type ::= ('full-time' | 'part-time')
    exp_phrase ::= 'paid' + ['professional'] + 'experience'
    location ::= 'with the city of los angeles'
    as_phrase ::= 'as' + 'an?'
    job ::= ('accounting clerk'|'management assistant'|...)
    job_location ::= as_phrase + [location] + job + [location]
    experience ::= exp_number + time_period + of + exp_type + exp_phrase +
        job_location
    '''
    number = pyp.Optional('1.')
    exp_number_list = [n2w(i) for i in range(36)]
    exp_number = pyp.oneOf(exp_number_list)
    time_period = pyp.oneOf(['year', 'years', 'month', 'months'])
    of = pyp.Literal('of')
    exp_type = pyp.oneOf(['full-time', 'part-time'])
    exp_phrase = pyp.Literal('paid') + pyp.Optional('professional') + \
        pyp.Literal('experience')
    location = 'with the city of los angeles'
    as_phrase = pyp.Regex('as an?')
    job = pyp.oneOf(job_titles)
    # job = pyp.oneOf(['accounting clerk', 'senior management analyst'])
    job_location = pyp.Optional(location) + as_phrase + job + \
        pyp.Optional(location)
    experience = number + exp_number + time_period + of + exp_type + \
        exp_phrase + job_location
    return experience


def _parse_experience_ebnf(experience_parser, experience: str) -> List:
    if experience:
        try:
            experience_parts = experience_parser.parseString(experience)
            return experience_parts
        except pyp.ParseException:
            pass
    return []


def parse_experience(text: str, job_titles: List[str]):
    experience_parts = _parse_experience_ebnf(
        _get_experience_parser(job_titles), text)
    return experience_parts


num2words = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
             6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
             11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
             15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
             19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty',
             50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty',
             90: 'ninety', 0: 'zero'}


def n2w(n):
    try:
        return num2words[n]
    except KeyError:
        try:
            return num2words[n - n % 10] + ' ' + num2words[n % 10].lower()
        except KeyError:
            print('exp_number out of range')


def main():
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
