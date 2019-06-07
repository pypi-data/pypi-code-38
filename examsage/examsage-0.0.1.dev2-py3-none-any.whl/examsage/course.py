# Course level attributes
class Course(object):
    """Create a course"""
    def __init__(self, ID='', name='', term='', kind=''):
        self.ID = ID
        self.name = name
        self.term = term
        self.kind = kind
        self.assessments = []

    def add_assessment(self, assessment):
        self.assessments.append(assessment)
        assessment.course = self