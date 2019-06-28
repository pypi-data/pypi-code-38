from .row import Row, Header, LineBreak
from .cell import Cell
from .exceptions import TableEmptyError

class Table:

    def __init__(self, *args, **kwargs):
        '''Returns a new Table instance

        Arguments:
            hborder     - Single character used to draw horizontal border
            vborder     - Single character used to draw vertical border
            fgcolor     - Foreground colour to print table in
            bgcolor     - Background colour to print table in
            align       - Where to align text in table
            bold        - Display text in table bold
            dark        - Use a darker shade of the supplied fgcolor
        '''

        self.kwargs = {}
        self.kwargs['hborder'] = kwargs.get('hborder', '-')
        self.kwargs['vborder'] = kwargs.get('vborder', '|')
        self.kwargs['fgcolor'] = kwargs.get('fgcolor', None)
        self.kwargs['bgcolor'] = kwargs.get('bgcolor', None)
        self.kwargs['align']   = kwargs.get('align', 'left')
        self.kwargs['bold']    = kwargs.get('bold', False)
        self.kwargs['dark']    = kwargs.get('dark', False)

        self.rows = []

    def add_row(self, cells, **kwargs):
        '''Add a row to the table

        Arguments:
            cells       - List of Cell objects or strings
            header      - Treat row as a header
            fgcolor     - Foreground color to use when printing text
            bgcolor     - Background color to use when printing text
            align       - Where to align text in the Row
            bold        - Display text in row as bold
            italic      - Display text in row in italics
        '''

        if kwargs.get('header', False) and 'bold' not in kwargs:
            kwargs['bold'] = True
            self.rows.append(Header(self, cells, **kwargs))

        else:
            self.rows.append(Row(self, cells, **kwargs))

    def add_linebreak(self, character, **kwargs):
        '''Add a linebreak to the table

        Arguments:
            character   - Single character to use as a line break
            fgcolor     - Foreground colour to use when printing
            bgcolor     - Background colour to use when printing
            bold        - Display text as bold
            dark        - User a darker shade of the supplied fgcolor
        '''

        self.rows.append(LineBreak(self, [character], **kwargs))

    def column_width(self, column_index):
        '''Return width of given column'''

        cells = []
        for row in self.rows:
            try:
                cells.append(len(row.cells[column_index].text))
            except IndexError:
                cells.append(0)

        return max(cells)

    def as_string(self):
        '''Return table as a string to be printed'''

        if not self.rows:
            raise TableEmptyError('Unable to print empty table')

        output = []
        for row in self.rows:
            output.append(row.as_string())

        return '\n' + '\n'.join(output) + '\n'

    def __str__(self):
        return self.as_string()
