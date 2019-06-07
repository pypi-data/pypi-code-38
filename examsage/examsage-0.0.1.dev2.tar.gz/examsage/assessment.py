from examsage.body import Body
from examsage.headfoot import HeadFoot
from examsage.problem import Problem
from pylatex import Document, Command, Package, PageStyle, MdFramed
from pylatex.base_classes import Arguments
from pylatex.utils import NoEscape

class Assessment(Document):
    """A latex document for writing Math assessments."""

    tex_packages = ('assessments', 'mathexam', 'mathdiagrams')

    def __init__(
        self,
        kind=None,
        number=None,
        fullpoints=None,
        period=None,
        head_height = '30pt',
        instructions=None,
        hints=None,
        nameline=True,
        body=None,
    ):
        # Create the pylatex Document
        super().__init__(
            documentclass='article',
            document_options='12pt',
            geometry_options={'left':'0.5in', 'right':'0.5in', 'top':'1in', 'bottom':'1in'},
            page_numbers=True,
            indent=False,
        )
        self.kind = kind
        self.number = number
        self.fullpoints = fullpoints
        self.period = period
        #self.instructor_key = instructor_key # Used in Assessment.dumps()
        self.head_height = head_height
        self.instructions = instructions
        self.hints = hints
        self.nameline = nameline
        self.headfoot = HeadFoot(name='default', assessment=self)
        self.body = body
        # Publish the last version by default
        #self.versions = []
        self.version = 0

        for name in Assessment.tex_packages:
            self.packages.append(Package(name))

    @property
    def instructions(self):
        return self.__instructions

    @instructions.setter
    def instructions(self, instructions):
        # Print the instructions inside of a frame
        if instructions:
            frame = MdFramed()
            frame.append(NoEscape(instructions))
            self.__instructions = frame
        else:
            self.__instructions = None

    @property
    def hints(self):
        return self.__hints

    @hints.setter
    def hints(self, hints):
        self.__hints = hints

    @property
    def instructor_key(self):
        return self.__instructor_key

    @instructor_key.setter
    def instructor_key(self, instructor_key):
        if isinstance(instructor_key, bool):
            self.__instructor_key = instructor_key
        else:
            print("The instructor key must be either 'True' or 'False'.")

    @property
    def headfoot(self):
        return self.__headfoot

    @headfoot.setter
    def headfoot(self, headfoot):
        if isinstance(headfoot, PageStyle) or headfoot == None:
            self.__headfoot = headfoot
        else:
            print("The headfoot must be an instance of pylatex.PageStyle")

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, body):
        if isinstance(body, Body):
            body.assessment = self
            self.__body = body
        elif body != None:
            print("The body must be an instance of examsage.Body")

    @property
    def maxpoints(self):
        return self.body.maxpoints

    #def dumps(self):
    #    return self.versions[self.version]

    def dumps(self):
        # Delete the old preamble
        self.preamble.clear()
        # Set the key flags
        if self.instructor_key:
            self.preamble.append(Command('setbool', Arguments('instructorKey', 'true')))
            self.preamble.append(Command('setbool', Arguments('studentKey', 'true')))
        else:
            self.preamble.append(Command('setbool', Arguments('instructorKey', 'false')))
            self.preamble.append(Command('setbool', Arguments('studentKey', 'false')))

        self.preamble.append(self.headfoot)
        self.change_length('\headheight', self.head_height)

        # Delete the old body
        self.clear()
        self.change_document_style(self.headfoot.name)
        # Update the body
        if self.nameline:
            # Add the name line
            self.append(Command('ExamNameLine'))

        if self.instructions:
            # Add the instructions
            self.append(self.instructions)

        if self.hints:
            # Add the hints
            self.append(self.hints)

        self.append(self.body)

        return super().dumps()

    def __next__(self):
        # Generate a similar assessment
        next(self.body)
        #self.versions.append(self.my_dumps())
        return self