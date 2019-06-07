from pylatex import Figure
from pylatex.utils import NoEscape
import pathlib

class FiniteTiles(Figure):
    """Inserts the finite tiles image."""

    _latex_name = 'figure'
    filename = pathlib.Path(__file__).parent / 'Images' / 'FiniteTiles.png'
    filename = str(filename)

    def __init__(self):
        super().__init__(position='h!')
        self.add_image(self.filename, width=NoEscape(r'\linewidth'))