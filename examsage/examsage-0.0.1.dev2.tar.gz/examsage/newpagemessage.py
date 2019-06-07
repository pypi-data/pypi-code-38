from pylatex import SmallText, NewLine, NewPage
from pylatex.base_classes import Container
from pylatex.utils import bold

class NewPageMessage(Container):
    """Appends a message before adding a new page to the document."""

    def __init__(self, message=r'Please continue on the next page.'):
        r"""
        Parameters
        ----------
        message: str
            The message to display before starting a new page.
        """

        self.message = message
        super().__init__(
            data=[
                #NewLine(),
                SmallText(bold(self.message)),
                NewPage(),
            ]
        )

    def dumps(self):
        r"""Represent the message and new page as a string in LaTeX syntax.

        Returns
        -------
        str
            A LaTeX string representing the message and new page.
        """

        # Have the Container construct the LaTeX string.
        return self.dumps_content()