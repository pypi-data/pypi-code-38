# -*- coding: utf-8 -*-

from datetime import date

from django.conf import settings


# http://192.168.0.10:8080/jasperserver/flow.html?_flowId=viewReportFlow&standAlone=true&reportUnit=/Imobiliar/Relatorios/Balancete_Por_Periodo&datafin=2016-01-31&dataini=2016-01-01&j_username=alugar&amp;j_password=consulta&amp;decorate=no

def montaURLjasperReport(report_name, params=None):
    """
        params:`dict`, ex: 'dataini':`datetime.datetime`(2016,5,1),'datafin':`datetime.datetime`(2016,5,31)}
    """
    if params is None:
        params = {}
    url_string = settings.REPORT_URI + '/flow.html?_flowId=viewReportFlow&standAlone=true&reportUnit=' + report_name

    paramstr = ''
    if type(params) == dict:
        for k, v in params.items():
            if isinstance(v, date):
                params[k] = v.strftime("%Y-%m-%d")
            else:
                params[k] = v
            p = '{0}={1}&'.format(k, v)
            paramstr += p
    else:
        raise TypeError("Params is not Dict Type")

    login = 'j_username={0}&j_password={1}&decorate=no'.format(settings.REPORT_USERNAME, settings.REPORT_PASSWORD)

    url = '{0}&{1}{2}'.format(url_string, paramstr, login)
    print('URL: ' + url)

    return url
