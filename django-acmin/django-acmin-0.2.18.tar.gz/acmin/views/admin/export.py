import datetime
import gzip

import xlwt
from django.http import HttpResponse
from django.utils.http import urlquote
from django.utils.six import BytesIO

from acmin.models import Permission, PermissionItem, Field
from acmin.utils import attr, display
from .list import AdminListView


class AdminExportView(AdminListView):
    paginate_by = None

    def has_permission(self):
        return Permission.has_permission(self.request.user, self.model, PermissionItem.exportable)

    def get_fields(self):
        return [field for field in Field.get_fields(self.request.user, self.model) if field.exportable]

    def get(self, request, *args, **kwargs):
        return self.export_excel(self.get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_type"] = 'export'
        return context

    def export_excel(self, objects):
        fields = self.get_fields()
        model_verbose = attr(self.model, '_meta.verbose_name')
        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet('%s列表' % model_verbose)
        style_heading = xlwt.easyxf("""
            font:name Arial,colour_index white,bold on,height 0xA0;
            align:wrap off,vert center,horiz center;
            pattern:pattern solid,fore-colour 0x19;
            borders:left THIN,right THIN,top THIN,bottom THIN;
            """)
        style_body = xlwt.easyxf("""
                font:name Arial,bold off,height 0XA0;
                align:wrap on,vert center,horiz left;
                borders:left THIN,right THIN,top THIN,bottom THIN;
                """)
        # style_green = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x11;")
        # style_red = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x0A;")
        fmts = [
            'M/D/YY', 'D-MMM-YY', 'D-MMM', 'MMM-YY',
            'h:mm AM/PM', 'h:mm:ss AM/PM', 'h:mm', 'h:mm:ss', 'M/D/YY h:mm', 'mm:ss', '[h]:mm:ss', 'mm:ss.0',
        ]
        style_body.num_format_str = fmts[0]

        for column, field in enumerate(fields):
            sheet.write(0, column, str(field.verbose), style_heading)

        for row, obj in enumerate(objects, 1):
            for column, field in enumerate(fields, 0):
                sheet.write(row, column, str(display(obj, field.name)), style_body)

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        response = HttpResponse(gzip.compress(buf.getvalue()), content_type="application/vnd.ms-excel")
        filename = model_verbose + "-" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        response['Content-Disposition'] = 'attachment;filename=%s.xls' % urlquote(filename)
        response['Content-Encoding'] = 'gzip'
        return response
