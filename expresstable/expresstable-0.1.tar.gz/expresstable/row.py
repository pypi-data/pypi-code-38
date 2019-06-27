from .cell import Cell

class Row:

    def __init__(self, parent, cells, **kwargs):
        '''Returns a new Row instance

        Arguments:
            parent      - Reference to Table
            cells       - List of cell objects or strings
            fgcolor     - Foreground colour to print row in
            bgcolor     - Background colour to print row in
            align       - Where to align text in row
            bold        - Display row text in bold
            dark        - Use a darker shade of the supplied fgcolor
        '''

        self.parent = parent
        self.kwargs = kwargs

        self.cells = []
        for item in cells:
            tmp_kwargs = {**self.parent.kwargs}
            tmp_kwargs.update(kwargs)
            if type(item) is not Cell:
                cell = Cell(item, **tmp_kwargs)
            else:
                tmp_kwargs.update(item.kwargs)
                cell = Cell(item.text, **tmp_kwargs)

            self.cells.append(cell)

    def as_string(self):
        '''Return Row object as a string'''

        row = []
        vborder = Cell(self.parent.kwargs['vborder'], **self.kwargs).as_string(0, '')
        for index, cell in enumerate(self.cells):
            row.append(cell.as_string(self.parent.column_width(index)))

        return ' ' + f'{vborder}'.join(row)

class Header(Row):

    def as_string(self):
        output = []
        border = [self.parent.kwargs['hborder'] for c in self.cells]
        output.append(LineBreak(self.parent, border, **self.kwargs).as_string())
        output.append(Row(self.parent, self.cells, **self.kwargs).as_string())
        output.append(LineBreak(self.parent, border, **self.kwargs).as_string())

        return '\n'.join(output)

class LineBreak(Row):

    def as_string(self):
        border_char = self.cells[0].text
        row = []
        for index, cell in enumerate(self.cells):
            row.append(Cell(border_char * self.parent.column_width(index), **self.kwargs).as_string(0, '-'))
            row.append(Cell(border_char, **self.kwargs).as_string(0, ''))

        return ' ' + ''.join(row[:-1]) + ' '
