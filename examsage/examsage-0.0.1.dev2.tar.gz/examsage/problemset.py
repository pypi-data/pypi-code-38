from examsage.problem import Problem
from pylatex import Enumerate, Package, Command
from pylatex.base_classes import Options

class ProblemSet(Enumerate):
    """An enumerate environment for enumerating Examsage.Problem() instances.

    Call ProblemSet.add_item(LatexObject) to add the object to a numbered list.
    Call ProblemSet.append(LatexObject) to add content that is not numbered.
    """

    _latex_name = 'enumerate'
    tex_packages = ('enumitem',
                   )

    def __init__(
        self,
        size=1,
        instructions=None,
        hints=None,
        nameline=True,
    ):
        self.size = size
        self.instructions = instructions
        self.hints = hints
        self.nameline = nameline
        # Create the pylatex Environment
        super().__init__(options=Options(leftmargin='*'))
        for name in ProblemSet.tex_packages:
            self.packages.append(Package(name))

    @property
    def maxpoints(self):
        return sum([sum(item.points) for item in self.data if isinstance(item, Problem)])

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
        self.__hints = NoEscape(hints)

    # Automatically numbers ExamSage.Problem instances, however, the user
    # may wish to create assessments without numbered problems. Also, this breaks
    # super().add_item, which calls self.append()
    #def append(self, item):
    #    if isinstance(item, Problem):
    #        print("Adding problem {}".format(item.points))
    #        self.append(Command('item'))
    #        self.append(item)
    #    else:
    #        print("Appending item {}".format(item.__class__))
    #        super().append(item)