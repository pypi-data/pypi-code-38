from datetime import datetime
from pylatex import PageStyle, Head, Foot, LineBreak, VerticalSpace, simple_page_number, SmallText, FootnoteText
from pylatex.utils import bold, NoEscape

class HeadFoot(PageStyle):
    """Header is a subclass of pylatex's PageStyle class"""

    def __init__(self, name, assessment, padding='1pt'):
        # Create the pylatex pagestyle that contains the header and footer
        super().__init__(name)
        self.assessment = assessment
        self.padding = padding

    def dumps(self):
        # Clear the old data
        self.clear()
        assessment = self.assessment

        if hasattr(self.assessment, 'course'):
            course = self.assessment.course
        else:
            course = None

        if course:
            # Create left header
            with self.create(Head('L')):
                self.append(course.name)
                self.append(LineBreak())
                self.append(SmallText(course.kind))
                self.append(self.padding)
        # Create center header
        with self.create(Head('C')):
            self.append(NoEscape(r'\ifbool{instructorKey}{'))
            self.append(SmallText(bold('FOR INSTRUCTORS ONLY')))
            self.append(LineBreak())
            self.append(SmallText(bold(f'(Max. of {assessment.maxpoints} points)')))
            self.append(NoEscape(r'}{}'))
            self.append(self.padding)
        # Create right header
        with self.create(Head('R')):
            self.append(f'{assessment.kind} {assessment.number}.{assessment.version} - {assessment.fullpoints} Points')
            self.append(LineBreak())
            self.append(SmallText(f'Assessing Period: {assessment.period}'))
            self.append(self.padding)
        if course:
            # Create left footer
            with self.create(Foot('L')):
                self.append(course.term)
        # Create center footer
        with self.create(Foot('C')):
            now = datetime.now().strftime('%Y%m%d%H%M')
            self.append(FootnoteText(now))
        # Create right footer
        with self.create(Foot('R')):
            self.append(simple_page_number())

        return super().dumps()

    @property
    def padding(self):
        return self.__padding

    @padding.setter
    def padding(self, tex_length):
        # Space between the header text and line
        self.__padding = VerticalSpace(tex_length)