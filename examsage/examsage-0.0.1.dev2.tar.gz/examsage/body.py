from examsage.problem import Problem
from pylatex import Enumerate, Package, Command
from pylatex.base_classes import Options

class Body(Enumerate):
    """An enumerate environment for enumerating Examsage.Problem() instances.

    Call ProblemSet.add_item(LatexObject) to add the object to a numbered list.
    Call ProblemSet.append(LatexObject) to add content that is not numbered.
    """

    _latex_name = 'enumerate'
    tex_packages = ('enumitem',
                   )

    def __init__(self):
        # Create the pylatex Environment
        super().__init__(options=Options(leftmargin='*'))
        for name in self.tex_packages:
            self.packages.append(Package(name))
        self.assessment = None

    @property
    def maxpoints(self):
        return sum([sum(item.points) for item in self.data if isinstance(item, Problem)])

    def __next__(self):
        problems = [item for item in self if isinstance(item, Problem)]
        for problem in problems:
            next(problem)

        return self

    @property
    def version(self):
        return self.assessment.version

    def dumps(self, *args, **kwargs):
        for item in self:
            if isinstance(item, Problem):
                item.version = self.version

        return super().dumps()

#    def append(self, item):
#        if isinstance(item, Problem):
#            item.assessment = self.assessment
#
#        return super().append(item)

#    def add_item(self, item):
#        if isinstance(item, Problem):
#            print(f"Assigned {self.assessment} to {item}")
#            item.assessment = self.assessment
#
#        return super().add_item(item)

#    def dumps(self):
#        # Ensure that each problem has generated `self.size` versions
#        problems = [item for item in self if isinstance(item, Problem)]
#        for problem in problems:
#            while len(problem.versions) < self.size:
#                next(problem)
#
#        return super().dumps()