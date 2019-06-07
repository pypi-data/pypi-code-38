from pylatex import MdFramed
from pylatex.utils import NoEscape

class Instructions(MdFramed):
    """An MdFramed environment containing the assessment instructions."""

    _latex_name = 'mdframed'
    def __init__(self, instructions):
        # Print the instructions inside of a frame
        super().__init__()
        self.append(NoEscape(instructions))