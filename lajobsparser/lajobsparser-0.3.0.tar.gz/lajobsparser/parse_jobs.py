import logging
import pathlib
import datetime

from typing import List
from typing import Any
from typing import Tuple
from typing import Optional

import re
import sys
import pandas as pd

import pyparsing as pyp

from collections import namedtuple


log = logging.getLogger(__name__)

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


def get_bulletin_headers_file(path: pathlib.Path) -> List[List]:
    ' return headers for one job bulletin text file'
    headers: List[List] = []

    def is_valid_first_header() -> bool:
        # first non-blank line is header (job title)
        return len(headers) == 0

    # The header only has upper case letters and symbols
    header_re = re.compile(r"^[A-Z0-9\t\/\(\):_'\- ]+$")

    def is_header(text: str) -> bool:
        return not header_re.match(text) is None

    with path.open(encoding="ISO-8859-1") as f:
        for idx, file_line in enumerate(f.readlines()):
            # print(idx, line[:20], end='')
            line = file_line.strip()
            # if not empty line
            if len(line) > 0:
                if is_header(line):
                    headers.append(line)
    # first job bulletin in the job class title
    return headers[1:]


def get_bulletin_headers(paths: List[pathlib.Path]) -> List[List]:
    ' return headers for job bulletins in all text files '

    headers = []
    for idx, path in enumerate(paths):
        headers.extend(get_bulletin_headers_file(path))
    return headers


def get_header_counts(header_df, header):
    return header_df.groupby(header).size()


def get_job_bulletins(paths: List[pathlib.Path]) -> pd.DataFrame:
    bulletin_df = get_job_info_df(paths)

    return bulletin_df

    invalid_job_class_title_df = bulletin_df[
        bulletin_df.job_class_title.str.find('Class Code') >= 0]
    log.info('invalid job titles: {}'.format(len(invalid_job_class_title_df)))
    log.debug(invalid_job_class_title_df)

    # check duplicate class codes
    class_code_num = bulletin_df.job_class_no.value_counts()
    duplicate_class_codes = class_code_num[class_code_num > 1]
    log.info('Duplicate class codes count {}'.format(
        len(duplicate_class_codes)))

    log.debug('Duplicate class codes')
    log.debug(duplicate_class_codes)

    problem_class_codes = bulletin_df[
        bulletin_df.job_class_no.isin(
            duplicate_class_codes.index
        )][['file_name', 'job_class_no']].sort_values(by='job_class_no')
    log.debug(problem_class_codes)
    return bulletin_df


def check_job_class_titles(title_df, bulletin_df):
    ' compare job titles from title file and job bulletin files '
    bulletin_job = set(bulletin_df.job_class_title)
    title_job = set(title_df.job_class_title)

    jobs_in_both = bulletin_job | title_job
    log.debug(jobs_in_both)

    all_jobs = bulletin_job & title_job
    log.debug(all_jobs)

    title_list_only = title_job - bulletin_job
    log.debug(title_list_only)

    bulletin_list_only = bulletin_job - title_job
    log.debug(bulletin_list_only)

    title_compare_df = pd.DataFrame({
        'jobs_in_both': len(jobs_in_both),
        'all_jobs': len(all_jobs),
        'jobs_in_title_list_only': len(title_list_only),
        'jobs_in_bulletin_list_only': len(bulletin_list_only)
    }, index=[0])
    log.info(title_compare_df)


def get_data_dictionary(data_dictionary_path: pathlib.Path) -> pd.DataFrame:
    ' retrieve the data dictionary kaggle_data_dictionary.csv as a data frame '
    data_dict_df = pd.read_csv(data_dictionary_path, header=0)
    columns = [name.replace(' ', '_') for name in data_dict_df.columns]
    data_dict_df.columns = columns
    return data_dict_df


def parse_field(pat_re: Any, text: str) -> Tuple[str, int, int]:
    pat = pat_re.search(text)
    if pat and len(pat.groups()) > 0:
        return pat.group(1), pat.start(1), pat.end(1)
    return '', -1, -1


def get_job_class_title(text: str) -> str:
    return text.strip()


job_class_no_start_re = re.compile('(Class[ \t]+Code:)')
job_class_no_end_re = re.compile('(Open Date:)', re.IGNORECASE)


def parse_job_class_no(text: str) -> Tuple[int, int, int]:
    job_class_no_start_tag, start1, end1 = parse_field(
        job_class_no_start_re, text)
    job_class_no_end_tag, start2, end2 = parse_field(job_class_no_end_re, text)

    if start1 >= 0 and start2 >= 0:
        job_class_no_str = text[start1:start2].strip()
        colon_idx = job_class_no_str.find(':')
        job_class_no = int(job_class_no_str[colon_idx + 1:])
        return job_class_no, start1, start2
    return -1, -1, -1


def open_date_to_datetime(date_str: str) -> Optional[datetime.datetime]:
    try:
        open_date = datetime.datetime.strptime(date_str, '%m-%d-%y')
        return open_date
    except ValueError:
        pass
    return None


open_date_start_re = re.compile('(Open Date:)', re.IGNORECASE)
open_date_end_re = re.compile('(ANNUAL ?SALARY)')
open_date_re = re.compile('Open Date: +([0-9]{1,2}-[0-9]{2}-[0-9]{2})',
                          re.IGNORECASE)


def parse_open_date(text: str) -> Tuple[Optional[datetime.datetime], int, int]:
    open_date_start_tag, start1, end1 = parse_field(open_date_start_re, text)
    open_date_end_tag, start2, end2 = parse_field(open_date_end_re, text)

    if start1 >= 0 and start2 >= 0:
        open_date_field = text[start1:start2].strip()
        open_date_str, start, end = parse_field(open_date_re, open_date_field)
        open_date = open_date_to_datetime(open_date_str)
        return open_date, start1, start2
    return None, -1, -1


annual_salary_start_re = re.compile('(ANNUAL ?SALARY)')
annual_salary_end_re = re.compile('(DUTIES|NOTE)')


def get_salary_range_list_parser():
    ''' Use pyparsing to process salary ranges

    converts from old-format to new-format

    "$90,118 (flat-rated)" to "90118"
    "$125,175 to $155,514" to "125175-155514"
    "$49,903 to $72,996 and $55,019 to $80,472" to "49903-72996|55019-80472"

    Extended Backus-Naur form grammar

    currency ::= '$'
    number ::= [0-9,]+
    salary ::= currency + number
    to ::= 'to'
    salary_range ::= salary + to + salary
    '''
    currency = pyp.Word('$')
    number = pyp.Word(pyp.nums + ',').setParseAction(
        lambda x: x[0].replace(',', ''))
    salary = currency + number
    to = pyp.Literal('to').setParseAction(lambda x: '-')
    salary_range = salary + pyp.Optional(to + salary)
    return salary_range


def parse_salary_ebnf(salary_parser, salary_str: str) -> List:
    if salary_str:
        try:
            salary_parts = salary_parser.parseString(salary_str)
            return salary_parts
        except pyp.ParseException:
            pass
    return []


dwp_salary_re = re.compile("Department of Water and Power (is|are)",
                           re.IGNORECASE)


def parse_annual_salary(text: str) -> Tuple[str, int, int]:
    salary_start_tag, start1, end1 = parse_field(annual_salary_start_re, text)
    salary_end_tag, start2, end2 = parse_field(annual_salary_end_re, text)

    if start1 >= 0 and start2 >= 0:
        salary_str = text[end1:start2].strip()

        # find the first salary
        salary_parts = parse_salary_ebnf(
            get_salary_range_list_parser(), salary_str)
        annual_salary = ''
        if salary_parts:
            annual_salary = ''.join(salary_parts)

        # find DWP salary if it exists
        dwp_annual_salary = ''
        pat = dwp_salary_re.search(salary_str)
        if pat:
            dwp_salary_str = salary_str[pat.end(0):]
            dwp_salary_parts = parse_salary_ebnf(
                get_salary_range_list_parser(), dwp_salary_str)
            if dwp_salary_parts:
                dwp_annual_salary = ''.join(dwp_salary_parts)
        return '|'.join([annual_salary, dwp_annual_salary]), start1, start2
    return '', -1, -1


job_duties_start_re = re.compile('(DUTIES)')
job_duties_end_re = re.compile('(REQUIREMENT)')


def parse_job_duties(text: str) -> Tuple[str, int, int]:
    job_duties_start_tag, start1, end1 = parse_field(job_duties_start_re, text)
    job_duties_end_tag, start2, end2 = parse_field(job_duties_end_re, text)

    if start1 >= 0 and start2 >= 0:
        return text[start1:start2].strip(), end1, start2
    return '', -1, -1


requirement_start_re = re.compile('(REQUIREMENT)')
requirement_end_re = re.compile('(PROCESS NOTE|NOTE)')
requirement1_re = re.compile('(requirements?/ ?minimum qualifications?)')
requirement2_re = re.compile('(requirements?)')


def parse_requirement(text: str) -> Tuple[str, int, int]:
    requirement_start_tag, start1, end1 = parse_field(
        requirement_start_re, text)
    requirement_end_tag, start2, end2 = parse_field(requirement_end_re, text)

    if start1 >= 0 and start2 >= 0:

        requirement_str = text[start1:start2].strip()
        requirement_str = ' '.join(requirement_str.lower().split())

        requirement_prefix = requirement1_re.search(requirement_str)
        if requirement_prefix and len(requirement_prefix.groups()) > 0:
            requirement_str = requirement_str[requirement_prefix.end(1):]
        else:
            requirement_prefix = requirement2_re.search(requirement_str)
            if requirement_prefix and len(requirement_prefix.groups()) > 0:
                requirement_str = requirement_str[requirement_prefix.end(1):]
        return requirement_str, end1, start2

    return '', -1, -1


JobInfo = namedtuple(
    'JobInfo', [
        'job_class_title', 'job_class_no', 'open_date', 'annual_salary',
        'requirement'
    ]
)


def get_job_info_file(file_text):
    '''
        Using the lower case column names from the data dictionary

        1	FILE_NAME
        2	JOB_CLASS_TITLE
        3	JOB_CLASS_NO
        4	REQUIREMENT_SET_ID
        5	REQUIREMENT_SUBSET_ID
        6	JOB_DUTIES
        7	EDUCATION_YEARS
        8	SCHOOL_TYPE
        9	EDUCATION_MAJOR
        10	EXPERIENCE_LENGTH
        11	FULL_TIME_PART_TIME
        12	EXP_JOB_CLASS_TITLE
        13	EXP_JOB_CLASS_ALT_RESP
        14	EXP_JOB_CLASS_FUNCTION
        15	COURSE_COUNT
        16	COURSE_LENGTH
        17	COURSE_SUBJECT
        18	MISC_COURSE_DETAILS
        19	DRIVERS_LICENSE_REQ
        20	DRIV_LIC_TYPE
        21	ADDTL_LIC
        22	EXAM_TYPE
        23	ENTRY_SALARY_GEN
        24	ENTRY_SALARY_DWP
        25	OPEN_DATE
    '''

    job_class_title = None
    job_class_no = None
    # requirement_set_id = None
    # requirement_subset_id = None
    job_duties = None
    # education_years = None
    # school_type = None
    # education_major = None
    # experience_length = None
    # full_time_part_time = None
    # exp_job_class_title = None
    # exp_job_class_alt_resp = None
    # exp_job_class_function = None
    # course_count = None
    # course_length = None
    # course_subject = None
    # misc_course_details = None
    # drivers_license_req = None
    # driv_lic_type = None
    # addtl_lic = None
    # exam_type = None
    # entry_salary_gen = None
    # entry_salary_dwp = None
    open_date = None

    annual_salary = None
    requirement = None

    def print_text(msg, text):
        print(msg, '|', text.strip().replace('\n', ' ')[:50])

    job_class_no, start, end = parse_job_class_no(file_text)
    if start >= 0:
        job_class_title = get_job_class_title(file_text[:start])

    new_start = end
    open_date, start, end = parse_open_date(file_text[new_start:])

    new_start = new_start + end
    annual_salary, start, end = parse_annual_salary(file_text[new_start:])

    new_start = new_start + end
    job_duties, start, end = parse_job_duties(file_text[new_start:])

    new_start = new_start + end
    requirement, start, end = parse_requirement(file_text[new_start:])

    if job_class_title is None:
        sys.exit('missing job_class_title')

    if job_class_no is None:
        sys.exit('missing job_class_no')

    if open_date is None:
        sys.exit('missing open_date')

    if annual_salary is None:
        sys.exit('missing annual_salary')

    if requirement is None:
        sys.exit('missing requirement')

    job_info = JobInfo(
        job_class_title, job_class_no, open_date, annual_salary, requirement)

    return job_info


skip_paths = [
    'Vocational Worker  DEPARTMENT OF PUBLIC WORKS.txt'
]


def get_job_info_df(paths: List[pathlib.Path]):
    job_info_list = []
    # for path in paths:
    for idx, path in enumerate(paths):
        if path.name in skip_paths:
            continue
        # print(idx, path)
        with path.open(encoding="ISO-8859-1") as f:
            job_info = get_job_info_file(f.read())
            job_info_list.append(job_info)

    return pd.DataFrame.from_records(
        data=job_info_list, columns=JobInfo._fields)
