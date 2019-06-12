import numpy as np
import pandas
from clarusui.layout import Element
from clarusui.gridvisualisationelement import GridViz
from clarusui import utils, templates as tmp

class Table(GridViz):
    def __init__(self, response, **options):
        super(Table, self).__init__(response, **options)
        #add a column with values from index at beginning
        #as we want to display these too
        self._data_frame.insert(0, self._data_frame.index.name,
                                self._data_frame.index)
        self._data_frame_numeric = self._data_frame.apply(lambda x: x.astype(str).str.replace(',', '')
                                                          .apply(pandas.to_numeric, errors='ignore'))
        floats = self._data_frame_numeric.select_dtypes(include=[np.number])
        min_cell_value = floats.values.min() if not floats.empty else 0
        max_cell_value = floats.values.max() if not floats.empty else 0
        self._max_abs_cell_value = max(abs(min_cell_value), abs(max_cell_value))
        hierarchical = options.pop('hierarchy', False)
        self._hierarchy_splitter = options.pop('hierarchySplitter', '.' if hierarchical else None)
        self.default_display_format = options.pop('defaultDisplayFormat', '{:,.0f}')
        self.column_display_formats = options.pop('columnDisplayFormats', None)
        self.column_colour_logic = options.pop('columnColourLogic', None)
        self.column_flash_colour_logic = options.pop('columnFlashColourLogic', None)
        self._set_headers(self._get_filtered_col_headers())
        self._set_rows()
        self.set_header_css_class(options.pop('headerCssClass', None))
        self.set_header_colour(options.pop('headerColour', None))
        self.set_enhanced(options.pop('enhanced', False))
        self.set_page_size(options.pop('pageSize', 15))
        self.add_custom_css({'margin-bottom' : '0'}) #remove extra margin
        self._init_paging()

    def set_enhanced(self, enhanced):
        if enhanced:
            self.add_css_class('table-enhanced')

    def set_page_size(self, size):
        self._page_size = size
        self.add_data_attributes({'data-page-length':size})

    def _init_paging(self):
        if not self._requires_paging():
            self.enable_paging(False)

    def enable_paging(self, enable):
        if not enable:
            self.add_data_attributes({'data-paging':'false', 'data-searching':'false'})

    def _requires_paging(self):
        if len(self.rows) > self._page_size:
            return True
        return False

    def set_style(self, style):
        super(Table, self).set_style(style)
        self.add_css_class(style.table_css_class)

    def _apply_colours(self, colours):
        self.set_header_colour(colours)
        return colours

    def set_header_css_class(self, header_css_class):
        if header_css_class is not None:
            for header in self.headers:
                header.set_css_class(header_css_class)

    def set_header_colour(self, colours):
        if colours is not None:
            if isinstance(colours, list):
                colour = colours[0]
            else:
                colour = colours
            for header in self.headers:
                header.set_bgcolour(colour)

    def set_column_header_colour(self, column, colour):
        header = self.headers[column]
        header.set_bgcolour(colour)

    def get_column_display_format(self, column_name):
        display_format = None
        if self.column_display_formats is not None:
            display_format = self.column_display_formats.get(column_name)

        if display_format is not None:
            return display_format
        return self.default_display_format

    def _get_column_colour_logic(self, column_name):
        if self.column_colour_logic is not None:
            return self.column_colour_logic.get(column_name)
        return None

    def _eval_column_colour_logic(self, column_name, cell_value):
        logic = self._get_column_colour_logic(column_name)
        if logic is not None:
            return logic(cell_value)
        return None

    def _get_column_flash_colour_logic(self, column_name):
        if self.column_flash_colour_logic is not None:
            return self.column_flash_colour_logic.get(column_name)
        return None

    def _eval_column_flash_colour_logic(self, column_name, cell_value):
        logic = self._get_column_flash_colour_logic(column_name)
        if logic is not None:
            return logic(cell_value)
        return None

    def _set_headers(self, headers):
        self.headers = []

        for header in headers:
            header_cell = Cell(header)
            self.headers.append(header_cell)

    def _index_of_column(self, header):
        full_headers = list(self._data_frame)
        return full_headers.index(header)

    def _index_of_row(self, header):
        full_headers = list(self._data_frame.index.values)
        return full_headers.index(header)

    def _get_last_move(self, row, col):
        if self.last_move_response is None:
            return None
        if (row not in self.last_move_response.get_row_headers() or
                col not in self.last_move_response.get_col_headers()):
            return None
        return self.last_move_response.get_float_value(row, col)

    #def get_col_headers(self):
    #    return self._parsed().get_col_headers(self.is_grid())

    def _set_rows(self):
        self.rows = []
        temp_rows = []
        row_idx = 0
        for row_header in self._get_filtered_row_headers():
            row_cells = []
            for header in self.headers:
                cell = Cell(self._get_value(row_header if self._data_frame.index.is_unique else
                                            row_idx, header.cellvalue if
                                            self._data_frame.index.is_unique else
                                            self._index_of_column(header.cellvalue)),
                            numberFormat=self.get_column_display_format(header.cellvalue))
                colour = self._eval_column_colour_logic(header.get_cell_value(),
                                                        cell.get_cell_value())
                if colour is not None:
                    cell.set_bgcolour(colour)

                flash_colour = self._eval_column_flash_colour_logic(header.get_cell_value(),
                                                                    cell.get_cell_value())
                if flash_colour is not None:
                    cell.set_flash(flash_colour)
                else:
                    #set_last_move turns flashing on by default
                    cell.set_last_move(self._get_last_move(row_header, header.get_cell_value()))
                row_cells.append(cell)
                if cell.is_numeric(): #right align number cells
                    header.add_custom_css({'text-align':'right'})
            #self.rows.append(r)
            row_element = Row(row_header, row_cells, hierachySplitter=self._hierarchy_splitter)
            temp_rows.append(row_element)
            row_idx += 1

        for temp_row in temp_rows:
            for temp_row_2 in temp_rows:
                if temp_row_2.parent_row_header == temp_row.row_header:
                    temp_row.add_child_row(temp_row_2)
                    self._drilldown_link = None #disable drilldown

            if temp_row.children:
                temp_row.add_pointer_styling()

            if not temp_row.has_parent_row():
                self.rows.append(temp_row)

    def get_cell(self, row, column):
        return self.rows[row].row_cells[column]

    def get_row(self, row):
        return self.rows[row]

    def toDiv(self):
        return tmp.TABLE_TEMPLATE.render(table=self)

    def toResponsiveDiv(self):
        return tmp.RESPONSIVE_TABLE_TEMPLATE.render(table=self)

    #will set a flag against any cell with country name match - allow per column/cell etc?
    def add_country_flags(self):
        for row in self.rows:
            for cell in row:
                cell_value = cell.get_cell_value()
                country_code = utils.get_country_code(cell_value)
                if country_code is not None:
                    cell.set_icon('flag-icon flag-icon-'+country_code.lower())

class Row(Element):
    def __init__(self, rowHeader, rowCells, hierachySplitter=None, **options):
        super(Row, self).__init__(None, **options)
        self._hierachy_splitter = hierachySplitter
        self.parent_row_header = None
        self._top_level_parent_row_header = None
        self.nesting_level = 0
        self.row_header = self._get_clean_row_header(rowHeader)
        self.row_cells = rowCells
        self._set_parent_row_header()
        self.children = []
        self._format_first_col()
        self._set_first_col_sort()

    def _get_clean_row_header(self, row_header):
        if self._hierachy_splitter is None:
            return row_header
        return row_header.replace(self._hierachy_splitter, '_').replace(' ', '')

    def _set_parent_row_header(self):
        if self._hierachy_splitter is None:
            return
        row_header_split = self.row_header.split('_')
        self._top_level_parent_row_header = row_header_split[0]
        self.nesting_level = len(row_header_split) - 1
        if len(row_header_split) > 1:
            prh = "_".join(row_header_split[0:len(row_header_split)-1])
            self.parent_row_header = prh

    def has_parent_row(self):
        return self.parent_row_header is not None

    def add_child_row(self, child_row):
        self.children.append(child_row)
        self.row_cells[0].set_icon('fa fa-plus-circle')

    def _format_first_col(self):
        if self.nesting_level > 0:
            self.row_cells[0].add_custom_css({'padding-left':str(self.nesting_level+0.75)+'rem'})
            split = self.row_cells[0].cellvalue.split('.')
            self.row_cells[0].cellvalue = split[len(split)-1]

    def _set_first_col_sort(self):
        if self._top_level_parent_row_header is not None:
            self.row_cells[0].set_ordering_value(self._top_level_parent_row_header)

    def add_pointer_styling(self):
        for cell in self.row_cells:
            cell.add_custom_css({'cursor':'pointer'})

    def toDiv(self):
        raise NotImplementedError("Table row not suitable for standalone usage")

class Cell(Element):
    def __init__(self, cellvalue, **options):
        super(Cell, self).__init__(None, **options)
        self.number_format = options.pop('numberFormat', '{:,.0f}')
        self.cellvalue = cellvalue
        self.set_ordering_value(cellvalue)
        self.icon_name = None
        self.icon_alignment = 'left'
        if self.is_numeric():
            self.add_custom_css({'text-align':'right'})

    def set_ordering_value(self, value):
        self.add_data_attributes({'data-order':value})

    def is_numeric(self):
        if self.cellvalue is None:
            return False
        try:
            float(str(self.cellvalue)) #cast to string as float(True) == 1
            return True
        except Exception:
            return False

    def set_number_format(self, number_format):
        self.number_format = number_format

    def set_icon(self, iconName, iconAlignment='left'):
        self.icon_name = iconName
        self.icon_alignment = iconAlignment

    def _iconify_cell(self, cell_value):
        if self.icon_name is None:
            return cell_value
        icon_code = '<i class="'+self.icon_name+'" aria-hidden="true"></i>'
        if self.icon_alignment == 'left':
            cell_value = icon_code + ' ' +cell_value
        else:
            cell_value = cell_value + ' ' +icon_code
        return cell_value

    def get_cell_value(self):
        cell_value = ''
        if self.is_numeric():
            cell_value = self.number_format.format(float(self.cellvalue))
        else:
            cell_value = self.cellvalue

        return self._iconify_cell(cell_value)

    def set_bgcolour(self, colour):
        super(Cell, self).set_bgcolour(colour)
        self.set_border_colour(colour)
        rgb_colour = utils.hex_to_rgb(colour)
        if rgb_colour is not None:
            luma = utils.get_luma(rgb_colour)
            if luma > 120: #may need to tweak threshold to taste
                self.add_custom_css({'color':'black'})
            else:
                self.add_custom_css({'color':'white'})

    def toDiv(self):
        raise NotImplementedError("Table cell not suitable for standalone usage")

class HeatMap(Table):

    def _get_column_colour_logic(self, column_name):
        if column_name == self.headers[0].cellvalue:
            return None
        return self._heat_colour

    def _heat_colour(self, cell_value):
        try:
            cell_value = float(cell_value.replace(',', ''))
        except Exception:
            return None
        if cell_value == 0:
            return '#FAFAFA'

        if cell_value < 0:
            heat_scale = utils.get_heat_scale('Blues')
        else:
            heat_scale = utils.get_heat_scale('Greens')

        scale_length = len(heat_scale)
        values = [0, abs(cell_value), float(self._max_abs_cell_value)]
        colours = pandas.cut(values, bins=scale_length, labels=heat_scale)
        return colours[1]
