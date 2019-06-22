import requests
import re


class Course(dict):
    def _number(self, raw):
        if raw is None:
            return None
        return int(raw)

    def __init__(self, raw):
        self.update(raw)
        self.update(self.__dict__)

        self.section_status = raw['cSectionStatus']
        self.active = self.section_status == 'A'
        self.moved_to_spring = self.section_status == 'B'
        self.cancelled = self.section_status == 'C'
        self.moved_to_fall = self.section_status == 'D'
        self.closed = self.section_status == 'E'
        self.number_changed = self.section_status == 'N'
        # the "class" field from the documentation is ignored because it seems useless and never actually appears.
        self.number = raw['courseNumber']
        self.name = self.title = raw['courseTitle']
        self.crn = self._number(raw['crn'])
        self.course_registration_number = self.crn
        self.department = raw['department']
        self.description = raw['description']
        # A list. See meanings of codes at https://developers.yale.edu/courses
        # TODO: give an easy way to programatically say what designation this is in plain English
        self.distributional_requirement_designation = raw['distDesg']
        self.final_exam = self._number(raw['finalExam'])
        self.instructors = raw['instructorList']
        self.instructor_upis = raw['instructorUPI']
        # TODO: give easily usable data on this, for example meets_monday boolean and storing times
        self.meeting_pattern = raw['meetingPattern']
        self.primary_course_number = raw['primXLst']
        self.school_code = raw['schoolCode']
        self.school_name = self.school_description = raw['schoolDescription']
        self.secondary_course_numbers = raw['scndXLst']
        self.section_number = self._number(raw['sectionNumber'])
        self.short_title = raw['shortTitle']
        self.subject_code = raw['subjectCode']
        self.subject_number = raw['subjectNumber']
        self.term_code = self._number(raw['termCode'])
        self.year, self.term = divmod(self.term_code, 10**2)

    @property
    def raw_description(self):
        return re.sub('<[^<]+?>', '', self.description)

    @property
    def code(self):
        return self.subject_code + str(self.number)


class YaleCourses:
    API_TARGET = 'https://gw.its.yale.edu/soa-gateway/course/webservice/index'
    TERM_NAMES = ['spring', 'summer', 'fall']

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get(self, params: dict = {}):
        """
        Make a GET request to the API.

        :param params: dictionary of custom params to add to request.
        """
        params.update({
            'apikey': self.api_key,
            'mode': 'json',
        })
        request = requests.get(self.API_TARGET, params=params)
        if request.ok:
            return request.json()
        else:
            # TODO: Can we be more helpful?
            raise Exception('API request failed. Data returned: ' + request.text)

    def courses(self, subject: str, year: int = None, term: int = None):
        """
        Generate a request to the API and fetch data on a desired set of courses.
        There are many options for how to identify a course through your parameters.
        :param subject: code of subject area for courses to search for. Example: ACCT, AFAM, PLSC, ENGL, EP&E, CPSC
        :param year: four-digit year of the term you're getting data on. API will use current year if not specified.abs
        :param term: term that course runs in. If not specified, the API will use the current default term (Spring or Fall).
                     This value changes to the next term on January 3rd and June 1st.
        """
        params = {
            'subjectCode': subject.upper(),
        }
        if year is not None:
            if term is None:
                raise ValueError('A term must be specified with a year.')
            if type(term) == str and term.isalpha():
                try:
                    term = self.TERM_NAMES.index(term.lower()) + 1
                except ValueError:
                    raise ValueError(term + ' is not a recognized term label. Valid options: ' + str(self.TERM_NAMES))
            params['termCode'] = str(year * 100 + term)
        return [Course(raw) for raw in self.get(params)]

    def course(self, code: str = None, subject: str = None, number: str = None, year: int = None, term: int = None):
        """
        Get data for a single course.
        You must specify either code or subject AND number.
        :param code: full code of a course, eg. CPSC201.
        :param subject: string identifier of course subject, eg. CPSC.
        :param course_number: number of course, eg. 201.
        """
        if code is None and (subject is None or number is None):
            raise ValueError('Either a code or subject AND number must be passed.')
        if code:
            # Break off subject name from start
            code = re.split('(\d+)', code)
            subject = code.pop(0)
            number = ''.join(code)
        courses = self.courses(subject, year, term)
        for course in courses:
            if course.number == number:
                return course
