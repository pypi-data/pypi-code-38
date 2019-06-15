"""
Affiliations are used across 4 different projects!
They're kept here as constants to ensure translation is properly done

Codes are used in:
- MITOC Trips:
    - `ws_participant.affiliation` (tracking affiliation, lottery weighting)
    - Creation of the CyberSource form (dictates payment values)
- MITOC Gear (`people_memberships.membership_type`)

String values are used in:
- MITOC Gear (`people.affiliation`)
- DocuSign (Affiliation radio buttions). Referenced in:
    - `mitoc-waiver`: JSON template
    - `mitoc-member`: Processing submitted forms
- MITOC Trips (updating `people.affiliation` directly)
"""
from collections import namedtuple


Affiliation = namedtuple('Affiliation', ['CODE', 'VALUE', 'ANNUAL_DUES'])

MIT_UNDERGRAD = Affiliation('MU', 'MIT undergrad', 15)
MIT_GRAD_STUDENT = Affiliation('MG', 'MIT grad student', 15)
MIT_AFFILIATE = Affiliation('MA', 'MIT affiliate', 30)
NON_MIT_UNDERGRAD = Affiliation('NU', 'Non-MIT undergrad', 40)
NON_MIT_GRAD_STUDENT = Affiliation('NG', 'Non-MIT grad student', 40)
MIT_ALUM = Affiliation('ML', 'MIT alum', 40)
NON_AFFILIATE = Affiliation('NA', 'Non-affiliate', 40)

# All affiliations _except_ for the deprecated student affiliation
ALL = [
    MIT_UNDERGRAD,
    MIT_GRAD_STUDENT,
    NON_MIT_UNDERGRAD,
    NON_MIT_GRAD_STUDENT,
    MIT_ALUM,
    MIT_AFFILIATE,
    NON_AFFILIATE,
]

# This status reflects a student where we don't know their affiliation!
# (MIT students are $15, other students are $40)
DEPRECATED_STUDENT = Affiliation('S', 'Student', 40)
