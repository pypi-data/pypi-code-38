# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

import os
import uuid

from django.conf import settings
from django.http import Http404
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

from bigtiger.forms.admins import form_admin
from bigtiger.forms.forms import ExcelImportForm, ExcelImportFormAdmin
from bigtiger.views.generic.base import PermissionMixin, PkContextMixin, MimeTypeContextMixin, UserLogMixin, permission
from bigtiger.views.generic.detail import SingleObjectTemplateResponseMixin
from bigtiger.excels import XlrdMixin
from bigtiger.core.exceptions import DBError, SuspiciousOperation, ImportDataError


class FormMixin(PermissionMixin, ContextMixin):
    form_class = None
    form_admin_class = None
    prefix = None
    initial = {}

    def get_initial(self):
        return self.initial.copy()

    def get_prefix(self):
        return self.prefix

    def get_form_class(self):
        return self.form_class

    def get_form_admin_class(self):
        return self.form_admin_class

    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'r': self.request,
            'c': self.kwargs
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

            if hasattr(self, 'fill_request_data'):
                fill_data = self.fill_request_data()
                kwargs['data'].update(fill_data)
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        context['permission'] = self.get_url_permission()
        return super(FormMixin, self).get_context_data(**context)

    def form_valid(self, form):
        pass

    def dispatch_handler(self, form, cd):
        pass

    def form_invalid(self, form):
        if settings.DEBUG:
            for k, v in form.errors.iteritems():
                print('%(field)s:%(error)s' % {'field': k, 'error': v})


class ProcessFormView(UserLogMixin, View):

    @permission
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        self.adminform = form_admin.register(form, self.get_form_admin_class())
        context = self.get_context_data(adminform=self.adminform)
        return self.render_to_response(context)

    @permission
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        result = {}
        if form.is_valid():
            cd = form.cleaned_data
            error_msg = None

            handler = self.dispatch_handler(form, cd)
            try:
                handler(cd)
            except (DBError, SuspiciousOperation) as e:
                error_msg = e.message
            except ImportDataError as e:
                error_msg = e.message
                result['PAGE_ERRORS'] = e.excel_errors
            except Exception as e:
                error_msg = '操作失败，请重试。'
                if settings.DEBUG:
                    print e.message

            if error_msg is None:
                result['successinfo'] = '操作成功。'
                self.success_log(self.request, cd, handler)
            else:
                result['errorinfo'] = error_msg
                self.error_log(self.request, cd, handler, error_msg)
        else:
            self.form_invalid(form)

        self.adminform = form_admin.register(form, self.get_form_admin_class())
        context = self.get_context_data(adminform=self.adminform, **result)
        return self.render_to_response(context)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormView(FormMixin, ProcessFormView):
    pass


class FormView(TemplateResponseMixin, BaseFormView):
    pass


class BaseCreateView(FormMixin, ProcessFormView):

    def get(self, request, *args, **kwargs):
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseCreateView, self).post(request, *args, **kwargs)

    def dispatch_handler(self, form, cd):
        return self.add

    def form_invalid(self, form):
        return super(BaseCreateView, self).form_invalid(form)


class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    pass


class BaseImportView(FormMixin, XlrdMixin, ProcessFormView):
    form_class = ExcelImportForm
    form_admin_class = ExcelImportFormAdmin
    sheet_index = 0
    start_line_number = 2

    def get_context_data(self, **kwargs):
        kwargs.update({'excel_template_name': self.excel_template_name})
        return FormMixin.get_context_data(self, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BaseImportView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseImportView, self).post(request, *args, **kwargs)

    def dispatch_handler(self, form, cd):
        import_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
        if not os.path.exists(import_dir):
            os.makedirs(import_dir)

        f = form.files['excel_file_file']
        file_path = os.path.join(
            import_dir, '%s%s' % (uuid.uuid4(), f.name))

        with open(file_path, 'wb+') as f1:
            for chunk in f.chunks():
                f1.write(chunk)

        data_lines, page_errors = self.read_xlsx(
            file_path, self.sheet_index, self.start_line_number)

        if page_errors:
            raise ImportDataError('数据格式不正确，修改后重试。', page_errors)

        def _import_data(cd):
            self.import_data(data_lines)

        return self._import_data

    def form_invalid(self, form):
        return super(BaseImportView, self).form_invalid(form)


class ImportView(SingleObjectTemplateResponseMixin, BaseImportView):
    template_name = 'admin/baseimport.htm'


class BaseUpdateView(FormMixin, PkContextMixin, ProcessFormView):
    pk_split_kwarg = '|'

    def get(self, request, *args, **kwargs):
        key = self.get_key()
        pks = self.get_pks()
        self.initial = self.get_init_form_data(key, pks)

        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

    def dispatch_handler(self, form, cd):
        return self.modify

    def form_invalid(self, form):
        return super(BaseUpdateView, self).form_invalid(form)


class UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView):
    pass


class MimeTypeView(PkContextMixin, MimeTypeContextMixin, UserLogMixin, ContextMixin, View):
    """ 通过MimeType实现视图
    """

    def _response(self, request, *args, **kwargs):
        key = self.get_key()
        pks = self.get_pks()
        mime_type = self.get_mime_type()

        error_msg = None
        cd = {'key': key, 'pks': pks}

        handler = getattr(self, mime_type, None)
        if handler is None:
            raise NotImplementedError(
                '%(handler)s未实现' % {'handler': mime_type})

        try:
            resp = handler(key, pks)
            if isinstance(resp, HttpResponse):
                return resp
        except (DBError, SuspiciousOperation) as e:
            error_msg = e.message
        except Exception as e:
            error_msg = '操作失败，请重试。'

        if error_msg is None:
            self.success_log(self.request, cd, handler)
            return JsonResponse({'success': True, 'message': '操作成功'})
        else:
            self.error_log(self.request, cd, handler, error_msg)
            return JsonResponse({'success': False, 'message': error_msg})


class MimeTypeGetView(MimeTypeView):

    def get(self, request, *args, **kwargs):
        return self._response(request, args, kwargs)


class MimeTypePostView(MimeTypeView):

    def post(self, request, *args, **kwargs):
        return self._response(request, args, kwargs)


class BaseDeleteView(MimeTypePostView):

    def get_mime_type(self):
        return 'delete'


class DeleteView(BaseDeleteView):
    pass
