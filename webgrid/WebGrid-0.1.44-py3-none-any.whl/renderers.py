from __future__ import absolute_import

import io
from operator import itemgetter
import warnings
from collections import defaultdict
import six
from six.moves import range

from blazeutils.containers import HTMLAttributes, LazyDict
from blazeutils.datastructures import BlankObject
from blazeutils.helpers import tolist
from blazeutils.jsonh import jsonmod
from blazeutils.spreadsheets import Writer, WriterX, xlsxwriter
from blazeutils.strings import reindent, randnumerics
import jinja2 as jinja
from webhelpers2.html import HTML as _HTML, literal, tags
from werkzeug import Href, MultiDict

from .extensions import (
    gettext as _,
    ngettext,
    translation_manager
)
from .utils import current_url
import csv

try:
    from morphi.helpers.jinja import configure_jinja_environment
except ImportError:
    configure_jinja_environment = lambda *args, **kwargs: None  # noqa: E731

try:
    from speaklater import is_lazy_string
except ImportError:
    is_lazy_string = lambda value: False  # noqa: E731

try:
    import xlwt
except ImportError:
    xlwt = None


def fix_xls_value(value):
    """
    Perform any data type fixes that must be made
    prior to sending a value to be written by the spreadsheet library
    """
    if is_lazy_string(value):
        return six.text_type(value)

    return value


class RenderLimitExceeded(Exception):
    pass


class HTML(object):
    # by default, the renderer will use the display value from the operator,
    # but that can be overriden by subclassing and setting this dictionary
    # like:
    #
    #   filtering_operator_labels['eq'] = 'equals'
    filtering_operator_labels = {}

    def __init__(self, grid):
        self.grid = grid
        self.manager = grid.manager
        if self.manager:
            self.jinja_env = self.manager.jinja_environment
        else:
            # if the grid is unmanaged for any reason (e.g. just not in a request/response
            # cycle and used only for render), fall back to a default jinja environment
            self.jinja_env = jinja.Environment(
                loader=jinja.PackageLoader('webgrid', 'templates'),
                autoescape=True
            )
        self.jinja_env.filters['wg_safe'] = jinja.filters.do_mark_safe

        configure_jinja_environment(self.jinja_env, translation_manager)

    def __call__(self):
        return self.render()

    def can_render(self):
        return True

    def render(self):
        if not self.can_render():
            raise RenderLimitExceeded('Unable to render HTML table')
        return self.load_content('grid.html')

    def grid_otag(self):
        return _HTML.div(_closed=False, **self.grid.hah)

    def grid_ctag(self):
        return literal('</div>')

    def header(self):
        if self.grid.hide_controls_box:
            return ''
        return self.load_content('grid_header.html')

    def header_form_otag(self, **kwargs):
        return _HTML.form(_closed=False, method='get', action=self.form_action_url(), **kwargs)

    def form_action_url(self):
        return self.reset_url(session_reset=False)

    def header_filtering(self):
        return self.load_content('header_filtering.html')

    def filtering_table_otag(self, **kwargs):
        kwargs.setdefault('cellpadding', 1)
        kwargs.setdefault('cellspacing', 0)
        return _HTML.table(_closed=False, **kwargs)

    def filtering_session_key(self):
        return _HTML.input(
            name='session_key',
            type='hidden',
            value=self.grid.session_key
        )

    def filtering_fields(self):
        rows = []
        for col in six.itervalues(self.grid.filtered_cols):
            rows.append(self.filtering_table_row(col))
        return literal('\n'.join(rows))

    def filtering_table_row(self, col):
        extra = getattr(col.filter, 'html_extra', {})
        return _HTML.tr(
            _HTML.th(self.filtering_col_label(col), class_='filter-label')
            + _HTML.td(self.filtering_col_op_select(col), class_='operator')
            + _HTML.td(
                _HTML.div(self.filtering_col_inputs1(col), class_='inputs1')
                + _HTML.div(self.filtering_col_inputs2(col), class_='inputs2')
            ),
            # Added _filter to address CSS collision with Bootstrap
            # Ref: https://github.com/level12/webgrid/issues/28
            class_=col.key + '_filter',
            **extra
        )

    def filtering_col_label(self, col):
        return col.label

    def filtering_col_op_select_options(self, filter):
        options = [tags.Option(literal('&nbsp;'), value='')]
        for op in filter.operators:
            options.append(tags.Option(
                self.filtering_operator_labels.get(op.key, op.display),
                value=op.key,
            ))
        return options

    def filtering_col_op_select(self, col):
        filter = col.filter
        if not filter.is_display_active:
            current_selected = ''
        else:
            current_selected = filter.op

        field_name = 'op({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        return tags.select(field_name, current_selected,
                           self.filtering_col_op_select_options(filter))

    def filtering_col_inputs1(self, col):
        filter = col.filter
        field_name = 'v1({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        inputs = ''
        if 'input' in filter.input_types:
            ident = '{0}_input1'.format(col.key)
            inputs += _HTML.input(name=field_name, type='text', value=filter.value1_set_with,
                                  id=ident)
        if 'select' in filter.input_types:
            ident = '{0}_select1'.format(col.key)
            current_selected = tolist(filter.value1) or []
            multiple = None
            if len(current_selected) > 1:
                multiple = 'multiple'
            inputs += tags.select(field_name, current_selected,
                                  self.filtering_filter_options(filter), multiple=multiple)
            inputs += self.filtering_toggle_image()
        return inputs

    def filtering_toggle_image(self):
        img_url = self.manager.static_url('bullet_toggle_plus.png')
        img_tag = tags.image(img_url, 'multi-select toggle', 16, 16, class_='toggle-button')
        return img_tag

    def filtering_filter_options(self, filter):
        # webhelpers2 doesn't allow options to be lists or tuples anymore. If this is the case,
        # turn it into an Option list
        return [
            (tags.Option(
                option[1],
                value=option[0]
            ) if isinstance(option, (tuple, list)) else option) for option in filter.options_seq
        ]

    def filtering_col_inputs2(self, col):
        filter = col.filter
        field_name = 'v2({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        # field will get modified by JS
        inputs = ''
        if 'input2' in filter.input_types:
            ident = '{0}_input2'.format(col.key)
            inputs += _HTML.input(name=field_name, type='text', value=filter.value2_set_with,
                                  id=ident)
        return inputs

    def filtering_add_filter_select(self):
        options = [tags.Option(literal('&nbsp;'), value='')]
        for col in six.itervalues(self.grid.filtered_cols):
            options.append(tags.Option(col.label, value=col.key))
        return tags.select('datagrid-add-filter', None, options)

    def filtering_json_data(self):
        for_js = {}
        for col_key, col in six.iteritems(self.grid.filtered_cols):
            for_js[col_key] = opdict = {}
            for op in col.filter.operators:
                opdict[op.key] = {
                    'field_type': op.field_type,
                    'hint': op.hint
                }
        return jsonmod.dumps(for_js)

    def confirm_export(self):
        count = self.grid.record_count
        if self.grid.unconfirmed_export_limit is None:
            confirmation_required = False
        else:
            confirmation_required = count > self.grid.unconfirmed_export_limit
        return jsonmod.dumps({
            'confirm_export': confirmation_required,
            'record_count': count
        })

    def header_sorting(self):
        return self.load_content('header_sorting.html')

    def sorting_select_options(self):
        options = [tags.Option(literal('&nbsp;'), value='')]
        for col in self.grid.columns:
            if col.can_sort:
                options.append(tags.Option(col.label, value=col.key))
                options.append(tags.Option(_('{label} DESC', label=col.label),
                                           value='-' + col.key))
        return options

    def sorting_select(self, number):
        key = 'sort{0}'.format(number)
        sort_qsk = self.grid.prefix_qs_arg_key(key)

        if len(self.grid.order_by) < number:
            currently_selected = ''
        else:
            currently_selected, flag_desc = self.grid.order_by[number - 1]
            if flag_desc:
                currently_selected = '-' + currently_selected
        return tags.select(sort_qsk, currently_selected, self.sorting_select_options())

    def sorting_select1(self):
        return self.sorting_select(1)

    def sorting_select2(self):
        return self.sorting_select(2)

    def sorting_select3(self):
        return self.sorting_select(3)

    def header_paging(self):
        return self.load_content('header_paging.html')

    def paging_select_options(self):
        options = []
        for page in range(1, self.grid.page_count + 1):
            label = _('{page} of {page_count}', page=page, page_count=self.grid.page_count)
            options.append(tags.Option(label, value=page))
        return options

    def paging_select(self):
        op_qsk = self.grid.prefix_qs_arg_key('onpage')
        return tags.select(op_qsk, self.grid.on_page, self.paging_select_options())

    def paging_input(self):
        pp_qsk = self.grid.prefix_qs_arg_key('perpage')
        return _HTML.input(type='text', name=pp_qsk, value=self.grid.per_page)

    def paging_url_first(self):
        return self.current_url(onpage=1, perpage=self.grid.per_page)

    def paging_img_first(self):
        img_url = self.manager.static_url('b_firstpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='<<')

    def paging_img_first_dead(self):
        img_url = self.manager.static_url('bd_firstpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='<<')

    def paging_url_prev(self):
        prev_page = self.grid.on_page - 1
        return self.current_url(onpage=prev_page, perpage=self.grid.per_page)

    def paging_img_prev(self):
        img_url = self.manager.static_url('b_prevpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='<')

    def paging_img_prev_dead(self):
        img_url = self.manager.static_url('bd_prevpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='<')

    def paging_url_next(self):
        next_page = self.grid.on_page + 1
        return self.current_url(onpage=next_page, perpage=self.grid.per_page)

    def paging_img_next(self):
        img_url = self.manager.static_url('b_nextpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='>')

    def paging_img_next_dead(self):
        img_url = self.manager.static_url('bd_nextpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='>')

    def paging_url_last(self):
        return self.current_url(onpage=self.grid.page_count, perpage=self.grid.per_page)

    def paging_img_last(self):
        img_url = self.manager.static_url('b_lastpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='>>')

    def paging_img_last_dead(self):
        img_url = self.manager.static_url('bd_lastpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='>>')

    def table(self):
        return self.load_content('grid_table.html')

    def no_records(self):
        return _HTML.p(_('No records to display'), class_='no-records')

    def table_otag(self, **kwargs):
        kwargs.setdefault('class_', 'records')
        return _HTML.table(_closed=False, **kwargs)

    def table_column_headings(self):
        headings = []
        for col in self.grid.iter_columns('html'):
            headings.append(self.table_th(col))
        th_str = '\n'.join(headings)
        th_str = reindent(th_str, 12)
        return literal(th_str)

    def table_th(self, col):
        label = col.label
        if self.grid.sorter_on and col.can_sort:
            url_args = {}
            url_args['dgreset'] = None
            url_args['sort2'] = None
            url_args['sort3'] = None
            cls = None
            if self.grid.order_by and len(self.grid.order_by) == 1:
                current_sort, flag_desc = self.grid.order_by[0]
                if current_sort == col.key:
                    cls = 'sort-' + ('desc' if flag_desc else 'asc')
                if current_sort != col.key or flag_desc:
                    url_args['sort1'] = col.key
                else:
                    url_args['sort1'] = '-{0}'.format(col.key)
            else:
                url_args['sort1'] = col.key
            label = _HTML.a(
                label,
                href=self.current_url(**url_args),
                class_=cls
            )
        return _HTML.th(label, **col.head.hah)

    def table_rows(self):
        rows = []
        # loop through rows
        for rownum, record in enumerate(self.grid.records):
            rows.append(self.table_tr(rownum, record))
        # process subtotals (if any)
        if rows and self.grid.subtotals in ('page', 'all') and \
                self.grid.subtotal_cols:
            rows.append(
                self.table_pagetotals(rownum + 1, self.grid.page_totals)
            )
        if rows and self.grid.subtotals in ('grand', 'all') and \
                self.grid.subtotal_cols:
            rows.append(
                self.table_grandtotals(rownum + 2, self.grid.grand_totals)
            )
        rows_str = '\n        '.join(rows)
        return literal(rows_str)

    def table_tr_styler(self, rownum, record):
        # handle row styling
        row_hah = HTMLAttributes()

        # add odd/even classes to the rows
        if (rownum + 1) % 2 == 1:
            row_hah.class_ += 'odd'
        else:
            row_hah.class_ += 'even'

        for styler in self.grid._rowstylers:
            styler(self.grid, rownum, row_hah, record)

        return row_hah

    def table_tr_output(self, cells, row_hah):
        # do some formatting so that the source code is properly indented
        tds_str = u'\n'.join(cells)
        tds_str = reindent(tds_str, 12)
        tds_str = u'\n{0}\n        '.format(tds_str)

        return _HTML.tr(literal(tds_str), **row_hah)

    def table_tr(self, rownum, record):
        row_hah = self.table_tr_styler(rownum, record)

        # get the <td>s for this row
        cells = []
        for col in self.grid.iter_columns('html'):
            cells.append(self.table_td(col, record))

        return self.table_tr_output(cells, row_hah)

    def table_totals(self, rownum, record, label, numrecords):
        row_hah = self.table_tr_styler(rownum, record)
        row_hah.class_ += 'totals'

        # get the <td>s for this row
        cells = []
        colspan = 0
        firstcol = True
        for col in self.grid.iter_columns('html'):
            if col.key not in list(self.grid.subtotal_cols.keys()):
                if firstcol:
                    colspan += 1
                else:
                    cells.append(_HTML.td(literal('&nbsp;')))
                continue
            if firstcol:
                bufferval = ngettext('{label} ({num} record):',
                                     '{label} ({num} records):',
                                     numrecords,
                                     label=label)
                buffer_hah = HTMLAttributes(
                    colspan=colspan,
                    class_='totals-label'
                )
                if colspan:
                    cells.append(_HTML.td(bufferval, **buffer_hah))
                firstcol = False
                colspan = 0
            cells.append(self.table_td(col, record))

        return self.table_tr_output(cells, row_hah)

    def table_pagetotals(self, rownum, record):
        return self.table_totals(rownum, record, _('Page Totals'), rownum)

    def table_grandtotals(self, rownum, record):
        count = self.grid.record_count
        return self.table_totals(rownum, record, _('Grand Totals'), count)

    def table_td(self, col, record):
        col_hah = HTMLAttributes(col.body.hah)

        # allow column stylers to set attributes
        for styler, cname in self.grid._colstylers:
            for_column = self.grid.column(cname)
            if col.key == for_column.key:
                styler(self.grid, col_hah, record)

        # extract the value from the record for this column and prep
        col_value = col.render('html', record, col_hah)

        # turn empty values into a non-breaking space so table cells don't
        # collapse
        if col_value is None:
            styled_value = literal('&nbsp;')
        elif isinstance(col_value, six.string_types) and col_value.strip() == '':
            styled_value = literal('&nbsp;')
        else:
            styled_value = col_value

        return _HTML.td(styled_value, **col_hah)

    def footer(self):
        return self.load_content('grid_footer.html')

    def load_content(self, endpoint, **kwargs):
        kwargs['renderer'] = self
        kwargs['grid'] = self.grid

        try:
            # give the adapter a chance to render
            if hasattr(self.grid.manager, 'render_template'):
                return self.grid.manager.render_template(endpoint, **kwargs)
        except jinja.exceptions.TemplateNotFound:
            # fail silently, will fail on the next step if there's really a problem
            pass

        # if the adapter doesn't want it, default to raw Jinja2
        template = self.jinja_env.get_template(endpoint)
        return template.render(**kwargs)

    def current_url(self, **kwargs):
        curl = current_url(self.grid.manager, strip_querystring=True, strip_host=True)
        href = Href(curl, sort=True)

        req_args = MultiDict(self.grid.manager.request_args())

        # kwargs will be modified with new keys if there is a prefix, so copy the original set
        # of keys first. Otherwise, the loop may pick up new keys and apply the prefix again
        key_list = list(kwargs.keys())
        for key in key_list:
            # arg keys may need to be prefixed
            if self.grid.qs_prefix:
                prefixed_key = self.grid.qs_prefix + key
                kwargs[prefixed_key] = kwargs[key]
                del kwargs[key]
                key = prefixed_key

            # multidicts extend, not replace, so we need to get rid of the
            # keys first
            try:
                del req_args[key]
            except KeyError:
                pass

        # convert to md first so that if we have lists in the kwargs, they
        # are converted appropriately
        req_args.update(MultiDict(kwargs))
        return href(req_args)

    def reset_url(self, session_reset=True):
        url_args = {}
        url_args['perpage'] = None
        url_args['onpage'] = None
        url_args['sort1'] = None
        url_args['sort2'] = None
        url_args['sort3'] = None
        url_args['export_to'] = None
        url_args['datagrid-add-filter'] = None

        for col in six.itervalues(self.grid.filtered_cols):
            url_args['op({0})'.format(col.key)] = None
            url_args['v1({0})'.format(col.key)] = None
            url_args['v2({0})'.format(col.key)] = None

        url_args['session_key'] = self.grid.session_key
        if session_reset:
            url_args['dgreset'] = 1

        return self.current_url(**url_args)

    def export_url(self, renderer):
        return self.current_url(export_to=renderer)

    def xls_url(self):
        warnings.warn('xls_url is deprecated. Use export_url instead.', DeprecationWarning)
        return self.export_url('xls')


class XLS(object):
    mime_type = 'application/vnd.ms-excel'

    def __init__(self, grid, max_col_width=150):
        self.grid = grid
        self.define_styles()
        self.col_contents_widths = defaultdict(int)
        self.max_col_width = max_col_width

    def __call__(self):
        return self.build_sheet()

    def can_render(self):
        total_rows = self.grid.record_count + 1
        if self.grid.subtotals != 'none':
            total_rows += 1
        return total_rows <= 65536 and sum(1 for _ in self.grid.iter_columns('xls')) <= 256

    def define_styles(self):
        self.style = BlankObject()
        self.style.bold = xlwt.easyxf('font: bold True;')

    def sanitize_sheet_name(self, sheet_name):
        return sheet_name if len(sheet_name) <= 30 else (sheet_name[:27] + '...')

    def build_sheet(self, wb=None, sheet_name=None):
        if xlwt is None:
            # !!!: translate?
            raise ImportError('you must have xlwt installed to use Excel renderer')

        if not self.can_render():
            raise RenderLimitExceeded('Unable to render XLS sheet')

        if wb is None:
            wb = xlwt.Workbook()
        sheet = wb.add_sheet(
            self.sanitize_sheet_name(sheet_name or self.grid.ident)
        )
        xlh = Writer(sheet)

        self.sheet_header(xlh)
        self.sheet_body(xlh)
        self.sheet_footer(xlh)
        self.adjust_col_widths(sheet)

        return wb

    def sheet_header(self, xlh):
        pass

    def sheet_body(self, xlh):
        self.body_headings(xlh)
        self.body_records(xlh)

    def sheet_footer(self, xlh):
        pass

    def register_col_width(self, col, value):
        if value is None:
            return
        self.col_contents_widths[col.key] = max(
            self.col_contents_widths[col.key],
            col.xls_width_calc(value)
        )

    def adjust_col_widths(self, ws):
        for idx, col in enumerate(self.grid.iter_columns('xls')):
            max_registered_width = self.col_contents_widths[col.key]
            final_width = min(max_registered_width, self.max_col_width)

            # width calculation is 1/256th of width of zero character, using the
            # first font that occurs in the Excel file
            # the following calculation seems to get it done alright
            ws.col(idx).width = int((final_width + 3) * 256)

    def body_headings(self, xlh):
        for col in self.grid.iter_columns('xls'):
            self.register_col_width(col, col.label)
            xlh.awrite(fix_xls_value(col.label), self.style.bold)
        xlh.newrow()

    def body_records(self, xlh):
        # turn off paging
        self.grid.set_paging(None, None)

        rownum = 0
        for rownum, record in enumerate(self.grid.records):
            self.record_row(xlh, rownum, record)

        # totals
        if rownum and self.grid.subtotals != 'none' \
                and self.grid.subtotal_cols:
            self.totals_row(xlh, rownum + 1, self.grid.grand_totals)

    def record_row(self, xlh, rownum, record):
        for col in self.grid.iter_columns('xls'):
            self.record_cell(xlh, col, record)
        xlh.newrow()

    def totals_row(self, xlh, rownum, record):
        colspan = 0
        firstcol = True
        totals_xf = xlwt.easyxf('font: bold on; border: top thin')
        for col in self.grid.iter_columns('xls'):
            if col.key not in list(self.grid.subtotal_cols.keys()):
                if firstcol:
                    colspan += 1
                else:
                    xlh.awrite('', totals_xf)
                continue
            if firstcol:
                numrecords = self.grid.record_count
                bufferval = ngettext('Totals ({num} record):',
                                     'Totals ({num} records):',
                                     numrecords)
                xlh.ws.write_merge(
                    xlh.rownum,
                    xlh.rownum,
                    xlh.colnum,
                    xlh.colnum + colspan - 1,
                    fix_xls_value(bufferval),
                    totals_xf
                )
                xlh.colnum = xlh.colnum + colspan
                firstcol = False
                colspan = 0
            self.total_cell(xlh, col, record)
        xlh.newrow()

    def record_cell(self, xlh, col, record):
        value = col.render('xls', record)
        self.register_col_width(col, value)
        stymat = col.xlwt_stymat_calc(value)
        xlh.awrite(fix_xls_value(value), stymat)

    def total_cell(self, xlh, col, record):
        value = col.render('xls', record)
        self.register_col_width(col, value)
        stymat = col.xlwt_stymat_init()
        stymat.font.bold = True
        stymat.borders.top = xlwt.Formatting.Borders.THIN
        xlh.awrite(fix_xls_value(value), stymat)

    def file_name(self):
        return '{0}_{1}.xls'.format(self.grid.ident, randnumerics(6))

    def as_response(self, wb=None, sheet_name=None):
        wb = self.build_sheet(wb, sheet_name)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return self.grid.manager.file_as_response(buffer, self.file_name(), self.mime_type)


class XLSX(object):
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def __init__(self, grid):
        self.grid = grid
        self.styles_cache = LazyDict()
        self._xlsx_format_cache = {}
        self.default_style = {}
        self.col_widths = {}

    def get_xlsx_format(self, wb, style_dict):
        """
        This method is meant to solve a major performance issue with how xlsxwriter manages formats.
        Xlsxwriter maintains a cache of formats, however generating the cache key is surprisingly
        expensive since it must join together every property of the format.

        The upshot of this is that if we have several columns with identical style properties but
        separate xlsxwriter Format objects, the cache key will have to be generated multiple times
        per cell. It is much faster to use the same Format object for all columns sharing the same
        style properties.

        See xlsxwriter.format::Format._get_xf_index for how the caching works.
        """
        key = tuple(sorted(style_dict.items(), key=itemgetter(0)))
        if key not in self._xlsx_format_cache:
            self._xlsx_format_cache[key] = wb.add_format(style_dict)
        return self._xlsx_format_cache[key]

    def style_for_column(self, wb, col):
        if col.key not in self.styles_cache:
            style_dict = getattr(col, 'xlsx_style', self.default_style).copy()
            if col.xls_num_format:
                style_dict['num_format'] = col.xls_num_format
            self.styles_cache[col.key] = self.get_xlsx_format(wb, style_dict)
        return self.styles_cache[col.key]

    def update_column_width(self, col, data):
        width = max((col.xls_width_calc(data), self.col_widths.get(col.key, 0)))
        self.col_widths[col.key] = width

    def adjust_column_widths(self, writer):
        for idx, col in enumerate(self.grid.iter_columns('xlsx')):
            if col.key in self.col_widths:
                writer.ws.set_column(idx, idx, self.col_widths[col.key])

    def build_sheet(self, wb=None, sheet_name=None):
        if xlsxwriter is None:
            raise ImportError('you must have xlsxwriter installed to use the XLSX renderer')

        if not self.can_render():
            raise RenderLimitExceeded('Unable to render XLSX sheet')

        if wb is None:
            buf = io.BytesIO()
            wb = xlsxwriter.Workbook(buf, options={'in_memory': True})

        sheet = wb.add_worksheet(self.sanitize_sheet_name(sheet_name or self.grid.ident))
        writer = WriterX(sheet)

        self.sheet_header(writer, wb)
        self.sheet_body(writer, wb)
        self.sheet_footer(writer, wb)
        self.adjust_column_widths(writer)

        return wb

    def __call__(self):
        buf = io.BytesIO()
        with xlsxwriter.Workbook(buf, options={'in_memory': True}) as wb:
            return self.build_sheet(wb)

    def can_render(self):
        total_rows = self.grid.record_count + 1
        if self.grid.subtotals != 'none':
            total_rows += 1
        return total_rows <= 1048576 and sum(1 for _ in self.grid.iter_columns('xlsx')) <= 16384

    def sanitize_sheet_name(self, sheet_name):
        return sheet_name if len(sheet_name) <= 30 else (sheet_name[:27] + '...')

    def sheet_header(self, xlh, wb):
        pass

    def sheet_body(self, xlh, wb):
        self.body_headings(xlh, wb)
        self.body_records(xlh, wb)

    def sheet_footer(self, xlh, wb):
        pass

    def body_headings(self, xlh, wb):
        heading_style = wb.add_format({'bold': True})
        for col in self.grid.iter_columns('xlsx'):
            xlh.awrite(fix_xls_value(col.label), heading_style)
            self.update_column_width(col, col.label)
        xlh.nextrow()

    def body_records(self, xlh, wb):
        # turn off paging
        self.grid.set_paging(None, None)

        rownum = 0
        for rownum, record in enumerate(self.grid.records):
            self.record_row(xlh, rownum, record, wb)

        # totals
        if rownum and self.grid.subtotals != 'none' and self.grid.subtotal_cols:
            self.totals_row(xlh, rownum + 1, self.grid.grand_totals, wb)

    def record_row(self, xlh, rownum, record, wb):
        for col in self.grid.iter_columns('xlsx'):
            value = col.render('xlsx', record)
            style = self.style_for_column(wb, col)
            xlh.awrite(fix_xls_value(value), style)
            self.update_column_width(col, value)
        xlh.nextrow()

    def totals_row(self, xlh, rownum, record, wb):
        colspan = 0
        firstcol = True
        base_style_attrs = {
            'bold': True,
            'top': 6  # Double think border
        }
        base_style = wb.add_format(base_style_attrs)
        for col in self.grid.iter_columns('xlsx'):
            if col.key not in list(self.grid.subtotal_cols.keys()):
                if firstcol:
                    colspan += 1
                else:
                    xlh.awrite('', base_style)
                continue
            if firstcol:
                numrecords = self.grid.record_count
                bufferval = 'Totals ({0} record{1}):'.format(
                    numrecords,
                    's' if numrecords != 1 else '',
                )
                if colspan > 1:
                    xlh.ws.merge_range(
                        xlh.rownum,
                        xlh.colnum,
                        xlh.rownum,
                        xlh.colnum + colspan - 1,
                        bufferval,
                        base_style
                    )
                    xlh.colnum = xlh.colnum + colspan
                else:
                    xlh.awrite(bufferval, base_style)

                firstcol = False
                colspan = 0

            style = base_style_attrs.copy()
            style.update(getattr(col, 'xlsx_style', self.default_style))
            style = wb.add_format(style)
            value = col.render('xlsx', record)
            xlh.awrite(fix_xls_value(value), style)
            self.update_column_width(col, value)

        xlh.nextrow()

    def file_name(self):
        return '{0}_{1}.xlsx'.format(self.grid.ident, randnumerics(6))

    def as_response(self, wb=None, sheet_name=None):
        wb = self.build_sheet(wb, sheet_name)
        if not wb.fileclosed:
            wb.close()
        wb.filename.seek(0)
        return self.grid.manager.file_as_response(wb.filename, self.file_name(), self.mime_type)


class CSV(object):
    mime_type = 'text/csv'

    def __init__(self, grid):
        self.grid = grid

    def __call__(self):
        return self.render()

    def render(self):
        self.output = six.StringIO()
        self.writer = csv.writer(self.output, delimiter=',', quotechar='"')
        self.body_headings()
        self.body_records()

    def file_name(self):
        return '{0}_{1}.csv'.format(self.grid.ident, randnumerics(6))

    def build_csv(self):
        self.render()
        byte_data = six.BytesIO()
        byte_data.write(self.output.getvalue().encode('utf-8'))
        return byte_data

    def body_headings(self):
        headings = []
        for col in self.grid.iter_columns('csv'):
            headings.append(col.label)
        self.writer.writerow(headings)

    def body_records(self):
        # turn off paging
        self.grid.set_paging(None, None)

        for rownum, record in enumerate(self.grid.records):
            row = []
            for col in self.grid.iter_columns('csv'):
                row.append(col.render('csv', record))
            self.writer.writerow(row)

    def as_response(self):
        buffer = self.build_csv()
        buffer.seek(0)
        return self.grid.manager.file_as_response(buffer, self.file_name(), self.mime_type)
