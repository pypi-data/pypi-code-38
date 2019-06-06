from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.gridvisualisationelement import GridViz
from clarusui.layout import Element
from clarusui import utils
import numpy as np
import pandas
from markupsafe import escape

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

tableTemplate = env.get_template('table.html')
responsiveTableTemplate = env.get_template('table_mobile_responsive.html')

class Table(GridViz):
    def __init__(self, response, **options):
        super(Table, self).__init__(response,**options)
        self._dataFrame.insert(0, self._dataFrame.index.name, self._dataFrame.index) #add a column with values from index at beginning as we want to display these too
        #self._dataFrameNumeric = self._dataFrame.str.replace(',', '').astype(float, errors='ignore')
        self._dataFrameNumeric = self._dataFrame.apply(lambda x: x.astype(str).str.replace(',','').apply(pandas.to_numeric, errors='ignore'))
        floats = self._dataFrameNumeric.select_dtypes(include=[np.number])
        minCellValue = floats.values.min() if not floats.empty else 0
        maxCellValue = floats.values.max() if not floats.empty else 0
        self._maxAbsCellValue = max(abs(minCellValue), abs(maxCellValue))
        hierarchical = options.pop('hierarchy', False)
        self._hierarchySplitter = options.pop('hierarchySplitter', '.' if hierarchical else None)
        self.defaultDisplayFormat = options.pop('defaultDisplayFormat', '{:,.0f}')
        self.columnDisplayFormats = options.pop('columnDisplayFormats', None)
        self.columnColourLogic = options.pop('columnColourLogic', None)
        self.columnFlashColourLogic = options.pop('columnFlashColourLogic', None)
        self._set_headers(self._get_filtered_col_headers())
        self._set_rows()    
        self.set_header_css_class(options.pop('headerCssClass', None))
        self.set_header_colour(options.pop('headerColour', None))
        self.set_enhanced(options.pop('enhanced', False))
        self.set_page_size(options.pop('pageSize', 15))
        self.add_custom_css({'margin-bottom' : '0'}) #remove extra margin 
        self._init_paging()
               
    def set_enhanced(self, enhanced):
        if enhanced == True:
            self.add_css_class('table-enhanced')
            
    def set_page_size(self, size):
        self._pageSize = size
        self._add_data_attributes({'data-page-length':size})
        
    def _init_paging(self):
        if not self._requires_paging():
            self.enable_paging(False)
        
    def enable_paging(self, enable):
        if not enable:
            self._add_data_attributes({'data-paging':'false', 'data-searching':'false'})
    
    def _requires_paging(self):
        if len(self.rows) > self._pageSize:
            return True
        return False
        
            
    def _set_style(self, style):
        super(Table, self)._set_style(style)
        self.add_css_class(style.tableCssClass)

            
    def _apply_colours(self, colours):
        self.set_header_colour(colours)
        return colours
        
        
    def set_header_css_class(self, headerCssClass):        
        if (headerCssClass is not None):
            for header in self.headers:
                header.set_css_class(headerCssClass)
                
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
                
    def get_column_display_format(self, columnName):
        displayFormat = None
        if self.columnDisplayFormats is not None:
            displayFormat = self.columnDisplayFormats.get(columnName)
        
        if displayFormat is not None:
            return displayFormat
        else:
            return self.defaultDisplayFormat
        
    def _get_column_colour_logic(self, columnName):
        if self.columnColourLogic is not None:
            return self.columnColourLogic.get(columnName)
        return None
    
    def _eval_column_colour_logic(self, columnName, cellValue):
        logic = self._get_column_colour_logic(columnName)
        if logic is not None:
            return logic(cellValue)
        return None
    
    def _get_column_flash_colour_logic(self, columnName):
        if self.columnFlashColourLogic is not None:
            return self.columnFlashColourLogic.get(columnName)
        return None
    
    def _eval_column_flash_colour_logic(self, columnName, cellValue):
        logic = self._get_column_flash_colour_logic(columnName)
        if logic is not None:
            return logic(cellValue)
        return None
                      
    def _set_headers(self, headers):
        self.headers = []
       
        for header in headers:
            headerCell = Cell(header)
            self.headers.append(headerCell)
            
    def _index_of_column(self, header):
        fullHeaders = list(self._dataFrame)
        return fullHeaders.index(header)
    
    def _index_of_row(self, header):
        fullHeaders = list(self._dataFrame.index.values)
        return fullHeaders.index(header)
    
    def _get_last_move(self, row, col):
        if self.lastMoveResponse is None:
            return None
        if row not in self.lastMoveResponse.get_row_headers() or col not in self.lastMoveResponse.get_col_headers():
            return None
        return self.lastMoveResponse.get_float_value(row, col)
        
    def get_col_headers(self):
        return self._parsed().get_col_headers(self.is_grid())
    
    def _set_rows(self):
        self.rows = []
        tempRows = []
        rowIdx = 0
        for row in self._get_filtered_row_headers():
            r = []
            for header in self.headers:
                cell = Cell(self._get_value(row if self._dataFrame.index.is_unique else rowIdx, 
                                            header.cellvalue if self._dataFrame.index.is_unique else self._index_of_column(header.cellvalue)), 
                            numberFormat=self.get_column_display_format(header.cellvalue))
                colour = self._eval_column_colour_logic(header.get_cell_value(), cell.get_cell_value())
                if colour is not None:
                    cell.set_bgcolour(colour)
                    
                flashColour = self._eval_column_flash_colour_logic(header.get_cell_value(), cell.get_cell_value())
                if flashColour is not None:
                    #cell.set_flash_colour(flashColour)
                    cell.set_flash(flashColour)
                else:
                    cell.set_last_move(self._get_last_move(row, header.get_cell_value())) #set_last_move turns flashing on by default
                    #cell.set_last_move(-100)
                    #cell.set_flash(period='3s', count=1)
                r.append(cell)
                if cell._is_numeric(): #right align number cells
                    header.add_custom_css({'text-align':'right'})
            #self.rows.append(r)
            rowElement = Row(row, r, hierachySplitter = self._hierarchySplitter)
            tempRows.append(rowElement)
            rowIdx += 1
            
        for tempRow in tempRows:
            for tempRow2 in tempRows:
                if tempRow2.parentRowHeader == tempRow.rowHeader:
                    tempRow.add_child_row(tempRow2)
                    self._drilldownLink = None #disable drilldown
                            
            if len(tempRow.children) > 0:    
                tempRow.add_pointer_styling()
            
            if tempRow.has_parent_row() == False:
                self.rows.append(tempRow)
    
    
    def get_cell(self, row, column):
        return self.rows[row].rowCells[column]
    
    def get_row(self, row):
        return self.rows[row]
    
    def toDiv(self):
        return tableTemplate.render(table=self)
    
    def toResponsiveDiv(self):
        return responsiveTableTemplate.render(table=self)
    
    #will set a flag against any cell with country name match - allow per column/cell etc?
    def add_country_flags(self):
        for row in self.rows:
            for cell in row:
                cv = cell.get_cell_value()
                countryCode = utils.get_country_code(cv)
                if countryCode is not None:
                    cell.set_icon('flag-icon flag-icon-'+countryCode.lower())
                    

class Row(Element):
    def __init__(self, rowHeader, rowCells, hierachySplitter=None, **options):
        super(self.__class__, self).__init__(None,**options)
        self._hierachySplitter = hierachySplitter
        self.parentRowHeader = None
        self._topLevelParentRowHeader = None
        self.nestingLevel = 0
        self.rowHeader = self._get_clean_row_header(rowHeader)
        self.rowCells = rowCells
        self._set_parent_row_header()
        self.children = []
        self._format_first_col()
        self._set_first_col_sort()
        
    def _get_clean_row_header(self, rowHeader):
        if self._hierachySplitter is None:
            return rowHeader
        return rowHeader.replace(self._hierachySplitter, '_').replace(' ', '')
           
        
    def _set_parent_row_header(self):
        if self._hierachySplitter is None:
            return
        rowHeaderSplit = self.rowHeader.split('_')
        self._topLevelParentRowHeader = rowHeaderSplit[0]
        self.nestingLevel = len(rowHeaderSplit) - 1
        if len(rowHeaderSplit) > 1:
            prh = "_".join(rowHeaderSplit[0:len(rowHeaderSplit)-1])
            self.parentRowHeader = prh
            
    def has_parent_row(self):
        return self.parentRowHeader != None
    
    def add_child_row(self, childRow):
        self.children.append(childRow)
        self.rowCells[0].set_icon('fa fa-plus-circle')
        
    def _format_first_col(self):
        if self.nestingLevel > 0:
            self.rowCells[0].add_custom_css({'padding-left':str(self.nestingLevel+0.75)+'rem'})
            split = self.rowCells[0].cellvalue.split('.')
            self.rowCells[0].cellvalue = split[len(split)-1]
    
    def _set_first_col_sort(self):
        if self._topLevelParentRowHeader is not None:
            self.rowCells[0]._set_ordering_value(self._topLevelParentRowHeader)
            
    def add_pointer_styling(self):
        for cell in self.rowCells:
            cell.add_custom_css({'cursor':'pointer'})
            
    def toDiv(self):
        raise NotImplementedError("Table row not suitable for standalone usage")
        
class Cell(Element):
    def __init__(self, cellvalue, **options):
        super(self.__class__, self).__init__(None,**options)
        self.numberFormat = options.pop('numberFormat', '{:,.0f}')
        self.cellvalue = cellvalue
        self._set_ordering_value(cellvalue)
        self.iconName = None
        self.iconAlignment = 'left'
        if self._is_numeric():
            self.add_custom_css({'text-align':'right'})
            
    def _set_ordering_value(self, value):
        self._add_data_attributes({'data-order':value})
    
    def _is_numeric(self):
        if self.cellvalue is None:
            return False
        try:
            x = float(str(self.cellvalue)) #cast to string as float(True) == 1
            return True
        except Exception:
            return False
    
    def set_number_format(self, numberFormat):
        self.numberFormat = numberFormat;
    
    def set_icon(self, iconName, iconAlignment='left'):
        self.iconName = iconName
        self.iconAlignment = iconAlignment
    
    def _iconify_cell(self, cellValue):
        if self.iconName is None:
            return cellValue
        iconCode = '<i class="'+self.iconName+'" aria-hidden="true"></i>'
        if self.iconAlignment == 'left':
            cellValue = iconCode + ' ' +cellValue
        else: 
            cellValue = cellValue + ' ' +iconCode
        return cellValue
            
    
    def get_cell_value(self):
        cv = ''
        if self._is_numeric():
            cv = self.numberFormat.format(float(self.cellvalue))
        else:
            cv = self.cellvalue
        
        return self._iconify_cell(cv)
    
    def set_bgcolour(self, colour):
        super(Cell, self).set_bgcolour(colour)
        self.set_border_colour(colour)
        rgbColour = self._hex_to_rgb(colour)
        if rgbColour is not None:
            luma = self._get_luma(rgbColour)
            if luma > 120: #may need to tweak threshold to taste
                self.add_custom_css({'color':'black'})
            else:
                self.add_custom_css({'color':'white'})
        
    def _hex_to_rgb(self, hexColour):
        if hexColour is not None and hexColour.startswith('#'):
            h = hexColour.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
    def _get_luma(self, rgbColour):
        luma = (0.2126 * rgbColour[0])  + (0.7152 * rgbColour[1]) + (0.0722 * rgbColour[2]);
        return luma
            
    def toDiv(self):
        raise NotImplementedError("Table cell not suitable for standalone usage")
    
class HeatMap(Table):
    def __init__(self, response, **options):
        super(HeatMap, self).__init__(response,**options)    
        
    def _get_column_colour_logic(self, columnName):
        if columnName == self.headers[0].cellvalue:
            return None
        return self._heat_colour
    
    def _heat_colour(self, cellValue):
        try:
            cellValue = float(cellValue.replace(',',''))
        except:
            return None
        if cellValue == 0:
            return '#FAFAFA'
        
        if cellValue < 0:
            heatScale = utils.get_heat_scale('Blues')
        else: 
            heatScale = utils.get_heat_scale('Greens')
        
        scaleLength = len(heatScale)
        values = [0, abs(cellValue), float(self._maxAbsCellValue)]
        colours = pandas.cut(values, bins=scaleLength, labels=heatScale)
        return colours[1]
        
        
        
    
