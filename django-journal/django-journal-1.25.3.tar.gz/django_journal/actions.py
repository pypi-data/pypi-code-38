import csv


from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import exceptions


from . import models

def export_as_csv_generator(queryset):
    header = ['time', 'tag', 'message']
    tags = set(models.Tag.objects.filter(objectdata__journal__in=queryset).values_list('name', flat=True))
    for tag in list(tags):
        tags.add('%s__id' % tag)
    tags |= set(models.Tag.objects.filter(stringdata__journal__in=queryset).values_list('name', flat=True))
    extra_headers = map(lambda s: s.encode('utf-8'), sorted(tags))
    yield header+extra_headers
    for journal in queryset:
        row = {
                'time': journal.time.isoformat(' '),
                'tag': journal.tag.name.encode('utf-8'),
                'message': unicode(journal).encode('utf-8'),
              }
        for stringdata in journal.stringdata_set.all():
            row_name = stringdata.tag.name.encode('utf-8')
            row[row_name] = stringdata.content.encode('utf-8')
        for objectdata in journal.objectdata_set.all():
            row_name = objectdata.tag.name.encode('utf-8')
            row[row_name+'__id'] = str(objectdata.object_id)
            if objectdata.content_object is None:
                row[row_name] = '<deleted>'
            else:
                row[row_name] = unicode(objectdata.content_object).encode('utf-8')
        yield row

def export_as_csv(modeladmin, request, queryset):
    """
    CSV export for journal
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=journal.csv'
    l = export_as_csv_generator(queryset)
    header = l.next()
    writer = csv.DictWriter(response, header)
    writer.writerow(dict(zip(header, header)))
    for row in l:
        writer.writerow(row)
    return response
export_as_csv.short_description = _(u"Export CSV file")
