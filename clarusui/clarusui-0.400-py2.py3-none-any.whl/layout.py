import os
from abc import ABCMeta, abstractmethod
import webbrowser
from markupsafe import escape
from lxml import html, etree
from premailer import Premailer
from clarus.models import ApiResponse
import clarus
from clarusui import style as st, templates as tmp

ASSIGNED_IDS = {}
def create_element_id(element):
    element_class = type(element).__name__
    if ASSIGNED_IDS.get(element_class) is None:
        ASSIGNED_IDS[element_class] = 0

    element_idx = ASSIGNED_IDS.get(element_class)
    new_id = str(element_class)+'_'+str(element_idx)
    ASSIGNED_IDS[element_class] = element_idx + 1
    return new_id

class Element(object):
    __metaclass__ = ABCMeta
    def __init__(self, response, **options):
        self.id = create_element_id(self)
        self._set_inputs(response)
        self._set_drilldown(options)
        self._set_realtime(options)
        self._set_poll(options)
        self._set_stats(options)
        self.set_css_class(options.pop('cssClass', ''))
        self.set_size(options.pop('size', None))
        self.set_custom_css(options.pop('customCss', None))
        self.set_height(options.pop('height', None))
        self.background_colour = None
        self.font_colour = None
        self.border_colour = None
        self.set_bgcolour(options.get('bgcolour'))
        self.set_border_colour(options.pop('borderColour', None))
        self.options = dict(options)
        self.set_header(options.pop('header', ''))
        self._colours = None
        self.set_colours(options.pop('colours', None))
        self._event = options.get('event')
        self._data_atrributes = {}
        self.hot_flash_colour = '#76FF03'
        self.cool_flash_colour = '#00E5FF'
        self.last_move = None

    def set_event(self, event):
        self._event = event

    def _set_inputs(self, response):
        self.last_move_response = None
        self.other_responses = []
        if type(response) in [tuple, list]:
            real_time = self._extract_response_by_context(response, 'realtime')
            if real_time is not None:
                self.response = real_time

            last_move = self._extract_response_by_context(response, 'lastmove')
            if last_move is not None:
                self.last_move_response = last_move

            for resp in response:
                if resp.context is not None and resp.context.lower() != 'realtime':
                    self.other_responses.append(resp)
        else:
            self.response = response

    @staticmethod
    def _extract_response_by_context(full_response, context):
        for resp in full_response:
            if resp.context is not None and resp.context.lower() == context.lower():
                return resp
        return None

    def set_last_move(self, last_move=None, flash=True):
        self.last_move = last_move
        if flash:
            self.enable_last_move_flash()

    def _get_auto_style(self):
        if self._event is not None:
            style = st.get_auto_style(self._event, self._colours)
            return style
        return None

    def set_colours(self, colours):
        if self._colours is None:
            self._colours = self._apply_colours(colours)

    def _apply_colours(self, colours):
        return colours

    def get_id(self):
        return self.id

    def _set_realtime(self, options):
        realtime_grid = options.pop('realtime', None)
        if realtime_grid is not None and isinstance(realtime_grid, ApiResponse):
            self._realtime_grid_id = realtime_grid.stats.get('GridId')
        else:
            self._realtime_grid_id = options.pop('realtimeGridId', None)

    def _set_poll(self, options):
        self._poll_period = options.pop('pollPeriod', None)

    def _set_stats(self, options):
        self._stats = options.pop('stats', None)

    def listens_to_realtime(self, grid_id):
        self._realtime_grid_id = grid_id

    def _set_drilldown(self, options):
        self._drilldown_link = None
        drilldown_to = options.pop('drilldownTo', 'grid')

        if drilldown_to.lower() == 'charm':
            if (isinstance(self.response, ApiResponse) and
                    self.response.get_result_title() is not None):
                charm_screen = self.response.get_result_title().split(' ')[0]
                self._drilldown_link = 'RiskRequest:'+charm_screen
        elif drilldown_to.lower() == 'grid':
            grid_id = self._get_drilldown_grid_id(options)
            if grid_id is not None:
                drilldown_title = self._get_drilldown_title(options)
                self._drilldown_link = ('RiskRequest:DV01:gridId='+str(grid_id)+
                                        ';_breadcrumb=true;_title='+drilldown_title)
        else:
            self._drilldown_link = drilldown_to

    def _get_drilldown_grid_id(self, options):
        grid_id = options.pop('drilldownGridId', None)
        if grid_id is None:
            grid_id = self.get_grid_id()
        return grid_id

    def get_grid_id(self):
        if isinstance(self.response, ApiResponse):
            return self.response.stats.get('GridId')
        return None

    @staticmethod
    def _get_drilldown_title(options):
        title = options.pop('drilldownTitle', None)
        if title is None:
            title = options.get('title', None)
        if title is None:
            title = 'Drilldown'
        return title

    def _get_rgbcolour(self, colour):
        return colour

    def __str__(self):
        return self.toHTML()

    @abstractmethod
    def toDiv(self):
        pass

    def toResponsiveDiv(self):
        return self.toDiv()

    def toFinalElement(self):
        final_html = None
        if self._drilldown_link is None:
            final_html = self.toDiv()
        else:
            final_html = tmp.ANCHOR_TEMPLATE.render(content=self.toDiv(), link=self._drilldown_link)
        return final_html

    def _add_rt(self, result):
        result_meta = {}
        result_attribs = {}
        result_meta['gridId'] = self._realtime_grid_id
        result_attribs['isGrid'] = True
        result_attribs['subscriptions'] = [{'type':'Grid', 'ref':self._realtime_grid_id}]
        result['resultMeta'] = result_meta
        result['resultAttribs'] = result_attribs
        return result

    def _add_poll(self, result):
        result_attribs = {}
        result_attribs['subscriptions'] = [{'type':'Timer', 'ref':self._poll_period}]
        result['resultAttribs'] = result_attribs
        return result


    def _add_stats(self, result):
        result['resultStats'] = self._stats
        return result

    def add_meta(self, result):
        return result

    def get_meta(self):
        if self._event is not None:
            return self._event.get('__eventoriginmeta')
        return None

    def _build_json_response(self, final_html):
        result = {}
        result['resultData'] = final_html

        if self._realtime_grid_id is not None:
            result = self._add_rt(result)
        elif self._poll_period is not None: #only set if realtime not available
            result = self._add_poll(result)

        if self._stats is not None:
            result = self._add_stats(result)

        result = self.add_meta(result)

        return result


    def toFile(self):
        temp_file_name = 'temp-element.html'
        with open(temp_file_name, 'w') as f:
            f.write(self.toHTML())

        url = 'file://' + os.path.abspath(temp_file_name)
        webbrowser.open(url)
        return url


    def toHTML(self, event=None):
        ASSIGNED_IDS.clear()
        final_html = None
        if self._event is not None:
            event = self._event
        if (event is not None and clarus.get_output_type(event) is not None and
                (clarus.get_output_type(event) == 'email' or
                 clarus.get_output_type(event) == 'mail')):
            final_html = self.toInlinedHTML()
        else:
            final_html = self.toStandardHTML()

        if ((self._realtime_grid_id is None and self._stats is None and
             self._poll_period is None) or event is None or not clarus.is_gui_call(event)):
            return final_html
        return self._build_json_response(final_html)

    def _render(self, div):
        return tmp.BASE_TEMPLATE.render(content=div, element=self)

    def toStandardHTML(self):
        self.add_custom_css({'min-height':'100vh'}) #should be the final step to fill viewport
        return self._render(div=self.toDiv())

    def toInlinedHTML(self):
        self.add_custom_css({'min-height':'100vh'})#fill viewport
        html_out = self._render(div=self.toResponsiveDiv())
        html_out = html_out.replace('rem;', 'em;')
        html_out = html_out.replace('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">', '')
        converter = Premailer(html_out, disable_leftover_css=False,
                              keep_style_tags=True,
                              preserve_inline_attachments=False,
                              remove_classes=False,
                              disable_validation=True,
                              cssutils_logging_level='CRITICAL')
        dirty_html = converter.transform(pretty_print=False)
        doc = html.fromstring(dirty_html)
        head = doc.find('.//head')
        head.clear()
        head.append(etree.fromstring('<style>.table th{border:0px !important} .alert{padding-left:0rem !important; padding-right:0rem !important; display:inline-block !important; text-align:center !important;} @media only screen and (max-width:768px)  {.dashboard{overflow-x:auto !important} .alert{padding-top:0.5rem !important; padding-bottom:0.5rem !important; margin-bottom:0.5rem !important} .alert div{font-size:1.5rem !important;} h1{font-size:1.5rem !important} .wrapper{display: block !important;} .table th, .table td{font-size:14px !important} .mobile-only{display:block !important} .desktop-only{ display: none !important; }} @media only screen and (min-width:767px) {.mobile-only{ display: none !important; }}</style>'))

        for element in doc.cssselect('script'):
            element.drop_tree()
        result = html.tostring(doc, encoding='unicode')
        result = result.replace('rem;', 'em;')
        return result

    def toCSV(self):
        return self.response.text

    def set_css_class(self, css_class):
        self.css_class = css_class

    def add_css_class(self, css_class):
        self.css_class = self.css_class + ' ' + css_class

    def set_flash_colour(self, flash_colour):
        self.cool_flash_colour = flash_colour
        self.hot_flash_colour = flash_colour
        self.set_flash(flash_colour)

    def set_cool_flash_colour(self, flash_colour):
        self.cool_flash_colour = flash_colour

    def set_hot_flash_colour(self, flash_colour):
        self.hot_flash_colour = flash_colour

    def _get_last_move_flash_colour(self):
        if self.last_move is None or self.last_move == 0:
            return None
        if self.last_move > 0:
            return self.hot_flash_colour
        return self.cool_flash_colour

    def enable_last_move_flash(self, period='3s', count=1, animation='pulse'):
        self.set_flash(self._get_last_move_flash_colour(), period, count, animation)

    def set_flash(self, colour=None, period='3s', count=1, animation='pulse'):
        if colour is not None:
            self.add_css_class('animated '+animation)
            self.add_custom_css({'--flash-colour':colour,
                                 '--flash-period':period, '--flash-count':count})

    def set_custom_css(self, custom_css):
        self._custom_css = {}
        if custom_css is not None:
            self._custom_css = custom_css

    def add_custom_css(self, custom_css):
        self._custom_css.update(custom_css)

    @property
    def custom_css(self):
        if not self._custom_css:
            return ''

        css = 'style='
        for key in self._custom_css:
            css = (css + escape(str(key).replace(' ', '')) +
                   ':' + escape(str(self._custom_css.get(key)).replace(' ', '')) + ';')
        return css


    def _get_filtered_custom_css(self, css_filter):
        if not self._custom_css:
            return ''

        if css_filter is None:
            return self.custom_css

        if not isinstance(css_filter, list):
            css_filter = css_filter.split(',')
        has_value = False
        css = 'style='
        for key in self._custom_css:
            if key in css_filter:
                css = (css + escape(key.replace(' ', '')) + ':' +
                       escape(self._custom_css.get(key)) + ';')
                has_value = True

        if has_value:
            return css
        return ''

    def add_data_attributes(self, attributes):
        self._data_atrributes.update(attributes)

    @property
    def data_attributes(self):
        attrib_string = ''
        if not self._data_atrributes:
            return attrib_string

        for key in self._data_atrributes:
            attrib_string = (attrib_string + escape(key) + '=' +
                             escape(str(self._data_atrributes.get(key)))+' ')
        return attrib_string

    def set_bgcolour(self, colour):
        if colour is not None:
            self.add_custom_css({'background-color':colour})
            self.background_colour = colour

    def set_size(self, size):
        if size is not None:
            if not isinstance(size, int):
                raise TypeError("size must be an integer")
            if size > 12 or size < 1:
                raise ValueError("size must be 1 <= x <= 12 when specified")
            self.max_width = str((size*100/12))+'%'
        self.size = size


    def set_height(self, height):
        if height is not None:
            self.add_custom_css({'overflow-y':'auto', 'max-height':height})

    def set_border_colour(self, colour):
        if colour is not None:
            self.add_custom_css({'border-color':colour})
            self.add_custom_css({'border-style':'solid'})
            self.add_custom_css({'border-width':'1px'})
            self.border_colour = colour

    def set_style(self, style):
        if 'background-color' not in self._custom_css:
            self.set_bgcolour(style.foreground_colour)
        if 'border-color' not in self._custom_css:
            self.set_border_colour(style.border_colour)
        if 'font-family' not in self._custom_css and 'color' not in self._custom_css:
            self.set_font(style)
        self.set_colours(style.colours)

    def set_font(self, style):
        if style is not None:
            self.add_custom_css({'color':style.font_colour})
            self.add_custom_css({'font-family':style.font_family})
            self.font_colour = style.font_colour

    def set_header(self, header):
        self._header = header

    def _get_header(self):
        return self._header

class Dashboard(Element):
    def __init__(self, *child_elements, **options):
        super(Dashboard, self).__init__(None, **options)
        self.display_header = options.pop('displayHeader', bool(self._get_header()))
        self._set_child_elements(child_elements)
        self.uniform_column_size = options.pop('uniformColumnSize', False)
        self._finalise_column_sizing()
        self.set_event(options.pop('event', None))
        style = options.pop('style', self._get_auto_style())
        if style is not None:
            self.set_style(style)

    def add_meta(self, result):
        for elements in self.child_elements:
            for element in elements:
                if isinstance(element, Element):
                    result = element.add_meta(result)

        return result

    def set_event(self, event):
        super(Dashboard, self).set_event(event)
        for elements in self.child_elements:
            for element in elements:
                if isinstance(element, Element):
                    element.set_event(event)


    def set_style(self, style):
        self.set_font(style)
        if 'background-color' not in self._custom_css:
            self.set_bgcolour(style.background_colour)
        if 'border-color' not in self._custom_css:
            self.set_border_colour(style.border_colour)
        if self.display_header:
            if 'background-color' not in self._header_element.custom_css:
                self._header_element.set_bgcolour(style.background_colour)
        for elements in self.child_elements:
            for element in elements:
                element.set_style(style)

    def _set_child_elements(self, child_elements):
        self.child_elements = []
        header_row = []

        if self.display_header:
            header_row.insert(0, self._create_header_element())

        if header_row:
            self.child_elements.append(header_row)

        for element in child_elements:
            if not isinstance(element, list):
                self.child_elements.append([element])
            else:
                self.child_elements.append(element)

    def _finalise_column_sizing(self):
        if self.uniform_column_size:
            self._uniform_column_size()
        else:
            self._auto_column_size()

    def _auto_column_size(self):
        for elements in self.child_elements:
            holder = []
            unsized_element_count = 0
            unpecified_size_remaining = 12

            for element in elements:
                if element.size is None:
                    unsized_element_count += 1
                else:
                    unpecified_size_remaining = unpecified_size_remaining - element.size
                holder.append(element)
            if unpecified_size_remaining < 0:
                raise ValueError("specified sizes must total to <= 12")

            if unsized_element_count > 0:
                unspecified_element_size = int(unpecified_size_remaining/unsized_element_count)
                for i in holder:
                    if i.size is None:
                        i.set_size(unspecified_element_size)

    def _uniform_column_size(self):
        max_no_of_columns = 1
        for elements in self.child_elements:
            if len(elements) > max_no_of_columns:
                max_no_of_columns = len(elements)

        for elements in self.child_elements:
            for element in elements:
                element.set_size(int(12/max_no_of_columns))

    def _create_header_element(self):
        header = Header(header=self._get_header())
        header.add_custom_css({'border-bottom-style':'solid',
                               'border-bottom-width':'1px', 'border-color':'#434857'})
        self._header_element = header
        return self._header_element

    def toDiv(self):
        return tmp.LAYOUT_TEMPLATE.render(dashboard=self)

    def toResponsiveDiv(self):
        return tmp.LAYOUT_RESPONSIVE_TEMPLATE.render(dashboard=self)

class Grid(Dashboard):
    def __init__(self, *childElements, **options):
        self.columns = options.pop('columns', 2)
        laid_out_children = self._layout_children(*childElements)
        super(Grid, self).__init__(uniformColumnSize=True, *laid_out_children, **options)

    def _layout_children(self, child_elements):
        chunks = self._chunk(child_elements, self.columns)
        return list(chunks)

    @staticmethod
    def _chunk(elements, number_of_columns):
        for i in range(0, len(elements), number_of_columns):
            yield elements[i:i + number_of_columns]

class Tabs(Element):
    def __init__(self, *childElements, **options):
        super(Tabs, self).__init__(None, **options)
        self._set_child_elements(childElements)
        style = options.pop('style', self._get_auto_style())
        if style is not None:
            self.set_style(style)

    def set_style(self, style):
        #self._fontColour = style.fontColour
        #self._borderColour = style.borderColour
        #self.set_bgcolour(style.backgroundColour)
        super(Tabs, self).set_style(style)
        self.add_custom_css({'border-bottom-color':style.border_colour})
        for elements in self.child_elements:
            elements.set_style(style)

    def _set_child_elements(self, child_elements):
        self.child_elements = []
        for element in child_elements:
            self.child_elements.append(element)

    def toDiv(self):
        return tmp.TABS_TEMPLATE.render(tabs=self)

class Header(Element):
    def __init__(self, **options):
        super(Header, self).__init__(None, **options)

    def toDiv(self):
        return tmp.HEADER_TEMPLATE.render(header=self)
