import mimetypes
import os
import subprocess
import tempfile
import urllib.parse

from django.conf import settings
from django.http import HttpResponse
from django.utils import translation
from django.views.generic.base import View


def read_file(path):
    with open(path, 'rb') as f:
        return f.read()


def content_disposition_encode(request, filename):
    # See http://greenbytes.de/tech/tc2231/#attwithfn2231utf8
    # if not isinstance(filename, unicode):
    #     filename = filename.decode('utf8')
    # quoted = urllib.quote(filename.encode('utf8'))

    quoted = urllib.parse.quote(filename)

    # TODO: remove line
    # return 'attachment; filename*=utf-8\'\'%s' % quoted
    return 'filename*=utf-8\'\'%s' % quoted

    # if 'MSIE' in request.META.get('HTTP_USER_AGENT', ''):
    #     return 'attachment; filename="%s"' % quoted
    # else:
    #     return 'attachment; filename*=utf-8\'\'%s' % quoted


def HttpDownloadResponse(request, content, filename):
    resp = HttpResponse(content, content_type=mimetypes.guess_type(filename)[0])
    resp['content-disposition'] = (
        content_disposition_encode(request, filename))
    return resp


class PDFReportView(View):
    report_name = None
    pdf_name = None
    report_parameters = {}
    additional_parms = []
    database = 'default'

    # def __init__(self, *args, **kwargs):
    #     self.database = kwargs.pop('database', default='default')
    #     super().__init__(*args, **kwargs)

    def report_kwargs(self, kwargs):
        params = []
        for k, v in kwargs.items():
            if isinstance(v, str):
                v = '"{0}"'.format(v)
            params.append('{0}={1}'.format(k, v))
        return params

    def report_parameters_args(self):
        # params = []
        # for k, v in self.report_parameters.items():
        #     if isinstance(v, str):
        #         v = '"{0}"'.format(v)
        #     params.append('{0}={1}'.format(k, v))
        # return params
        return self.report_kwargs(self.report_parameters)

    def get(self, request, *args, **kwargs):
        with tempfile.NamedTemporaryFile() as output_file:
            db_host = settings.DATABASES[self.database].get('HOST', 'localhost') or 'localhost'
            cmd = [os.path.join(settings.JASPERSTARTER_DIR, 'bin/jasperstarter'),
                   # '--locale', translation.get_language(),
                   'pr', os.path.join(settings.JASPERREPORTS_DIR, self.report_name),
                   '-f', 'pdf',
                   '-o', output_file.name,
                   '--jdbc-dir', os.path.join(settings.JASPERSTARTER_DIR, 'jdbc/'),
                   '-t', 'generic',
                   '--db-url', settings.JASPERSTARTER_URL[self.database],
                   '--db-driver', settings.JASPERSTARTER_DRIVER[self.database],
                   '-u', settings.DATABASES[self.database]['USER'],
                   '-p', settings.DATABASES[self.database]['PASSWORD'],
                   '-H', db_host,
                   '-n', settings.DATABASES[self.database]['NAME'],
                   '-r']
            if self.report_parameters or self.kwargs:
                cmd += ['-P']
            if self.report_parameters:
                    cmd += self.report_parameters_args()
            if self.kwargs:
                    cmd += self.report_kwargs(kwargs)
            cmd += self.additional_parms

            print(" ".join(cmd))

            p = subprocess.Popen(
                " ".join(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = p.communicate()
            if p.returncode:
                raise Exception(p.returncode, ' '.join(cmd), stdout, stderr)

            pdf = read_file('{}.pdf'.format(output_file.name))

        return HttpDownloadResponse(request, pdf, self.pdf_name)
