from pylatex import Command, NewPage, Package
from pylatex.base_classes import Container, Arguments, Options
from scipy.stats import norm as normal
import pathlib


class Ztable(Container):
    """Inserts a Ztable."""

    #filename = r'/home/user/examsage-dev/examsage/Images/Ztable.pdf'
    filename = pathlib.Path(__file__).parent / 'Images' / 'Ztable.pdf'
    filename = str(filename)

    def __init__(self):
        pdf_path = Arguments(self.filename)
        pdf_path.escape = False
        options = Options(pages=r'{1,2}')
        options.escape = False
        pdf_length = Arguments('-2')
        pdf_length.escape = False
        super().__init__(
            data=[
                NewPage(),
                Command('includepdf', pdf_path, options),
                Command('addtocounter', 'page', None, extra_arguments=pdf_length),
            ]
        )
        self.packages.append(Package('pdfpages'))

    def dumps(self):
        r"""Represent the message and new page as a string in LaTeX syntax.

        Returns
        -------
        str
            A LaTeX string representing the message and new page.
        """

        # Have the Container construct the LaTeX string.
        return self.dumps_content()

    def get_prob(self, z):
        """Calculates the probability for a given z-score.

        Parameters
        ----------
        z: float
            A z-score. This will be rounded to two decimal places to match the
            PDF z-table.

        Returns
        -------
        float
            The probability, rounded to 4 decimal places, for the given z-score.
        """

        z = round(z, 2)
        if z > 3.49:
            return 1.0
        elif z < -3.49:
            return 0.0
        else:
            return round(normal.cdf(z, 0, 1), 4)

    def get_zscore(self, p):
        """Calculates the z-score for a given probability.

        Parameters
        ----------
        float
            A probability. This will be rounded to 4 decimal places to match the
            PDF z-table.

        Returns
        -------
        z: float
            The z-score, rounded to two decimal places, for the given probability.
        """

        p = round(p, 4)
        return round(normal.ppf(p, 0, 1), 2)